import os
import json
import hashlib
from datetime import datetime
from core.db import get_db, ensure_repo, get_current_branch, get_branch_commit, set_branch_commit


def make_commit(message):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT file_path, file_hash FROM staging")
    staged = cursor.fetchall()

    if len(staged) == 0:
        db.close()
        return {
            "success": False,
            "message": "No files staged. Use 'vcs add .' first."
        }

    branch_name = get_current_branch()
    parent_id = get_branch_commit(branch_name)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    raw = message + timestamp + str(parent_id) + branch_name
    commit_id = hashlib.sha1(raw.encode()).hexdigest()[:7]

    parent_ids = [parent_id] if parent_id else []

    cursor.execute(
        "INSERT INTO commits (id, message, timestamp, parent_ids, branch_id) VALUES (?, ?, ?, ?, (SELECT id FROM branches WHERE name = ?))",
        (commit_id, message, timestamp, json.dumps(parent_ids), branch_name)
    )

    for row in staged:
        cursor.execute(
            "INSERT INTO commit_files (commit_id, file_path, file_hash) VALUES (?, ?, ?)",
            (commit_id, row["file_path"], row["file_hash"])
        )

    cursor.execute("DELETE FROM staging")

    db.commit()
    db.close()

    set_branch_commit(branch_name, commit_id)

    return {
        "success": True,
        "message": "Commit created",
        "commit": {
            "id": commit_id,
            "message": message,
            "timestamp": timestamp,
            "branch": branch_name,
            "parent_ids": parent_ids
        }
    }
