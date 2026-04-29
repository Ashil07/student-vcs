import os
import shutil
from core.db import get_db, ensure_repo, get_current_branch, get_branch_commit, set_branch_commit


def undo_last_commit():
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    db = get_db()
    cursor = db.cursor()

    branch_name = get_current_branch()
    current_commit_id = get_branch_commit(branch_name)

    if not current_commit_id:
        db.close()
        return {
            "success": False,
            "message": "No commits to undo"
        }

    cursor.execute("SELECT parent_ids FROM commits WHERE id = ?", (current_commit_id,))
    row = cursor.fetchone()
    if not row:
        db.close()
        return {
            "success": False,
            "message": "Commit not found"
        }

    import json
    parent_ids = json.loads(row["parent_ids"])

    if not parent_ids:
        db.close()
        return {
            "success": False,
            "message": "Cannot undo the first commit"
        }

    parent_id = parent_ids[0]

    cursor.execute("DELETE FROM commits WHERE id = ?", (current_commit_id,))
    db.commit()

    set_branch_commit(branch_name, parent_id)

    cursor.execute("SELECT file_path, file_hash FROM commit_files WHERE commit_id = ?", (parent_id,))
    files = cursor.fetchall()
    db.close()

    for row in files:
        object_path = os.path.join(".myvcs/objects", row["file_hash"])
        if os.path.exists(object_path):
            shutil.copy2(object_path, row["file_path"])

    return {
        "success": True,
        "message": "Last commit undone",
        "current_commit": parent_id
    }
