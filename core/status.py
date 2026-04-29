import os
from core.hasher import hash_file
from core.db import get_db, ensure_repo, get_current_branch, get_branch_commit


def get_status():
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT file_path, file_hash FROM staging")
    staged_rows = cursor.fetchall()
    staged = {row["file_path"]: row["file_hash"] for row in staged_rows}

    branch_name = get_current_branch()
    commit_id = get_branch_commit(branch_name)

    committed_files = {}
    if commit_id:
        cursor.execute("SELECT file_path, file_hash FROM commit_files WHERE commit_id = ?", (commit_id,))
        committed_rows = cursor.fetchall()
        committed_files = {row["file_path"]: row["file_hash"] for row in committed_rows}

    db.close()

    current_files = {}

    for root, dirs, files in os.walk("."):
        if ".myvcs" in root or ".git" in root:
            continue

        for name in files:
            if name == ".vcsignore" or name == ".gitignore":
                continue

            path = os.path.join(root, name)
            current_files[path] = hash_file(path)

    new_files = []
    modified_files = []
    deleted_files = []
    staged_files = []

    for path in current_files:
        if path in staged:
            staged_files.append(path)
        elif path not in committed_files:
            new_files.append(path)
        elif current_files[path] != committed_files[path]:
            modified_files.append(path)

    for path in committed_files:
        if path not in current_files:
            deleted_files.append(path)

    return {
        "success": True,
        "new": new_files,
        "modified": modified_files,
        "deleted": deleted_files,
        "staged": staged_files,
        "branch": branch_name,
        "commit_id": commit_id
    }
