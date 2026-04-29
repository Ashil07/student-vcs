import hashlib
import json
import os
import shutil
from datetime import datetime
from core.db import get_db, ensure_repo, get_current_branch, get_branch_commit, set_branch_commit


def merge_branch(source_branch):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    current = get_current_branch()
    if source_branch == current:
        return {
            "success": False,
            "message": "Cannot merge a branch into itself"
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT commit_id FROM branches WHERE name = ?", (source_branch,))
    source_row = cursor.fetchone()
    if not source_row:
        db.close()
        return {
            "success": False,
            "message": f"Branch '{source_branch}' does not exist"
        }

    source_commit = source_row["commit_id"]
    target_commit = get_branch_commit(current)

    if not source_commit:
        db.close()
        return {
            "success": False,
            "message": f"Branch '{source_branch}' has no commits"
        }

    if target_commit == source_commit:
        db.close()
        return {
            "success": True,
            "message": f"Already up to date with '{source_branch}'",
            "fast_forward": True
        }

    is_ancestor = _is_ancestor(cursor, source_commit, target_commit)

    if is_ancestor:
        cursor.execute(
            "UPDATE branches SET commit_id = ? WHERE name = ?",
            (source_commit, current)
        )
        db.commit()
        db.close()

        _restore_files(source_commit)

        return {
            "success": True,
            "message": f"Fast-forward merge: '{current}' is now at '{source_commit}'",
            "fast_forward": True,
            "commit_id": source_commit
        }

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw = f"Merge {source_branch} into {current}" + timestamp + target_commit + source_commit
    commit_id = hashlib.sha1(raw.encode()).hexdigest()[:7]

    parent_ids = []
    if target_commit:
        parent_ids.append(target_commit)
    parent_ids.append(source_commit)

    cursor.execute(
        "INSERT INTO commits (id, message, timestamp, parent_ids, branch_id) VALUES (?, ?, ?, ?, (SELECT id FROM branches WHERE name = ?))",
        (commit_id, f"Merge branch '{source_branch}' into {current}", timestamp, json.dumps(parent_ids), current)
    )

    source_files = _get_commit_files(cursor, source_commit)
    target_files = _get_commit_files(cursor, target_commit) if target_commit else {}

    merged_files = dict(target_files)
    merged_files.update(source_files)

    for path, file_hash in merged_files.items():
        cursor.execute(
            "INSERT INTO commit_files (commit_id, file_path, file_hash) VALUES (?, ?, ?)",
            (commit_id, path, file_hash)
        )

    cursor.execute(
        "UPDATE branches SET commit_id = ? WHERE name = ?",
        (commit_id, current)
    )

    db.commit()
    db.close()

    _restore_files(commit_id)

    return {
        "success": True,
        "message": f"Merged '{source_branch}' into {current}",
        "fast_forward": False,
        "commit_id": commit_id
    }


def _is_ancestor(cursor, potential_ancestor, descendant):
    """Check if potential_ancestor is in the history of descendant."""
    if not descendant or not potential_ancestor:
        return False
    if potential_ancestor == descendant:
        return True

    visited = set()
    queue = [descendant]

    while queue:
        commit_id = queue.pop(0)
        if commit_id in visited:
            continue
        visited.add(commit_id)

        if commit_id == potential_ancestor:
            return True

        cursor.execute("SELECT parent_ids FROM commits WHERE id = ?", (commit_id,))
        row = cursor.fetchone()
        if row and row["parent_ids"]:
            parents = json.loads(row["parent_ids"])
            queue.extend([p for p in parents if p])

    return False


def _get_commit_files(cursor, commit_id):
    if not commit_id:
        return {}
    cursor.execute("SELECT file_path, file_hash FROM commit_files WHERE commit_id = ?", (commit_id,))
    return {row["file_path"]: row["file_hash"] for row in cursor.fetchall()}


def _restore_files(commit_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT file_path, file_hash FROM commit_files WHERE commit_id = ?", (commit_id,))
    files = cursor.fetchall()
    db.close()

    for row in files:
        object_path = os.path.join(".myvcs/objects", row["file_hash"])
        if os.path.exists(object_path):
            os.makedirs(os.path.dirname(row["file_path"]), exist_ok=True)
            shutil.copy2(object_path, row["file_path"])
