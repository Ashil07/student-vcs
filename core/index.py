import os
from core.hasher import hash_file, atomic_copy
from core.db import OBJECTS_DIR, get_db, ensure_repo


def add_files(target="."):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    db = get_db()
    cursor = db.cursor()

    if target == ".":
        cursor.execute("DELETE FROM staging")
    added_files = []

    def _stage_file(path):
        if not os.path.exists(path) or os.path.isdir(path):
            return
        if os.path.basename(path) in (".vcsignore", ".gitignore"):
            return
        if ".myvcs" in path or ".git" in path:
            return
        file_hash = hash_file(path)
        object_path = os.path.join(OBJECTS_DIR, file_hash)
        if not os.path.exists(object_path):
            atomic_copy(path, object_path)
        cursor.execute(
            "INSERT OR REPLACE INTO staging (file_path, file_hash) VALUES (?, ?)",
            (path, file_hash)
        )
        added_files.append(path)

    if target == ".":
        for root, dirs, files in os.walk("."):
            if ".myvcs" in root or ".git" in root:
                continue
            for name in files:
                if name in (".vcsignore", ".gitignore"):
                    continue
                path = os.path.join(root, name)
                _stage_file(path)
    else:
        _stage_file(target)

    db.commit()
    db.close()

    return {
        "success": True,
        "message": "Files added",
        "files": added_files,
        "count": len(added_files)
    }
