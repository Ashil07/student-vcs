import json
from core.db import get_db, ensure_repo


def get_log():
    if not ensure_repo():
        return {
            "success": False,
            "message": "No commits found"
        }

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM commits ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    db.close()

    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "message": row["message"],
            "timestamp": row["timestamp"],
            "parent_ids": json.loads(row["parent_ids"]),
            "branch_id": row["branch_id"]
        })

    return {
        "success": True,
        "commits": history
    }
