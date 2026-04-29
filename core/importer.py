import os
import zipfile
import shutil
from core.db import VCS_DIR, OBJECTS_DIR, get_db, init_db


def import_repo(source_file):
    if not os.path.exists(source_file):
        return {
            "success": False,
            "message": f"File not found: {source_file}"
        }

    if os.path.exists(VCS_DIR):
        shutil.rmtree(VCS_DIR)

    os.mkdir(VCS_DIR)
    os.mkdir(OBJECTS_DIR)

    with zipfile.ZipFile(source_file, "r") as zipf:
        for item in zipf.namelist():
            if item.startswith("repo/"):
                target_path = item.replace("repo/", "", 1)
                if target_path:
                    zipf.extract(item, ".")
                    extracted = os.path.join(".", item)
                    if os.path.exists(extracted):
                        final_path = os.path.join(".", target_path)
                        os.makedirs(os.path.dirname(final_path), exist_ok=True)
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        shutil.move(extracted, final_path)

        for item in zipf.namelist():
            extracted = os.path.join(".", item)
            if os.path.exists(extracted) and item.startswith("repo/"):
                if os.path.isdir(extracted):
                    shutil.rmtree(extracted)
                else:
                    os.remove(extracted)

        repo_dir = os.path.join(".", "repo")
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

    if not os.path.exists(".myvcs/vcs.db"):
        init_db()

    # Restore working directory files from current branch's commit
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, commit_id FROM branches WHERE is_current = 1 LIMIT 1")
    branch_row = cursor.fetchone()

    if branch_row and branch_row["commit_id"]:
        cursor.execute(
            "SELECT file_path, file_hash FROM commit_files WHERE commit_id = ?",
            (branch_row["commit_id"],)
        )
        for file_row in cursor.fetchall():
            object_path = os.path.join(OBJECTS_DIR, file_row["file_hash"])
            if os.path.exists(object_path):
                os.makedirs(os.path.dirname(file_row["file_path"]), exist_ok=True)
                shutil.copy2(object_path, file_row["file_path"])

    db.close()

    return {
        "success": True,
        "message": f"Repository imported from {source_file}"
    }
