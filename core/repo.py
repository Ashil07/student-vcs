import os
from core.db import VCS_DIR, OBJECTS_DIR, init_db, get_db, set_config, set_current_branch


def init_repo():
    if os.path.exists(VCS_DIR):
        return {
            "success": False,
            "message": "Repository already initialized"
        }

    os.mkdir(VCS_DIR)
    os.mkdir(OBJECTS_DIR)

    init_db()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO branches (name, commit_id, is_current) VALUES (?, NULL, 1)", ("main",))
    db.commit()
    db.close()

    set_config("created", "true")

    return {
        "success": True,
        "message": "Repository initialized"
    }
