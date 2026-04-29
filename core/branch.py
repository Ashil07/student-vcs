import os
import shutil
from core.db import get_db, ensure_repo, get_current_branch, set_current_branch, get_branch_commit


def create_branch(name, from_commit=None):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM branches WHERE name = ?", (name,))
    if cursor.fetchone():
        db.close()
        return {
            "success": False,
            "message": f"Branch '{name}' already exists"
        }

    if from_commit is None:
        from_commit = get_branch_commit(get_current_branch())

    cursor.execute(
        "INSERT INTO branches (name, commit_id, is_current) VALUES (?, ?, 0)",
        (name, from_commit)
    )
    db.commit()
    db.close()

    return {
        "success": True,
        "message": f"Branch '{name}' created",
        "commit_id": from_commit
    }


def list_branches():
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, is_current FROM branches ORDER BY name")
    rows = cursor.fetchall()
    db.close()

    current = get_current_branch()
    branches = []
    for row in rows:
        branches.append({
            "name": row["name"],
            "current": bool(row["is_current"])
        })

    return {
        "success": True,
        "branches": branches,
        "current": current
    }


def switch_branch(name):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, commit_id FROM branches WHERE name = ?", (name,))
    row = cursor.fetchone()
    if not row:
        db.close()
        return {
            "success": False,
            "message": f"Branch '{name}' does not exist"
        }

    db.close()

    set_current_branch(name)

    commit_id = row["commit_id"]
    if commit_id:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT file_path, file_hash FROM commit_files WHERE commit_id = ?", (commit_id,))
        files = cursor.fetchall()
        db.close()

        for file_row in files:
            object_path = os.path.join(".myvcs/objects", file_row["file_hash"])
            if os.path.exists(object_path):
                os.makedirs(os.path.dirname(file_row["file_path"]), exist_ok=True)
                shutil.copy2(object_path, file_row["file_path"])

    return {
        "success": True,
        "message": f"Switched to branch '{name}'",
        "commit_id": commit_id
    }


def delete_branch(name):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    current = get_current_branch()
    if name == current:
        return {
            "success": False,
            "message": "Cannot delete the current branch"
        }

    if name == "main":
        return {
            "success": False,
            "message": "Cannot delete the default branch 'main'"
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM branches WHERE name = ?", (name,))
    if not cursor.fetchone():
        db.close()
        return {
            "success": False,
            "message": f"Branch '{name}' does not exist"
        }

    cursor.execute("DELETE FROM branches WHERE name = ?", (name,))
    db.commit()
    db.close()

    return {
        "success": True,
        "message": f"Branch '{name}' deleted"
    }
