import sqlite3
import os
import json
import threading

VCS_DIR = ".myvcs"
DB_PATH = ".myvcs/vcs.db"
OBJECTS_DIR = ".myvcs/objects"

_db_lock = threading.Lock()


def get_db():
    """Get a thread-safe database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database with all tables."""
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                commit_id TEXT,
                is_current INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS commits (
                id TEXT PRIMARY KEY,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                parent_ids TEXT NOT NULL DEFAULT '[]',
                branch_id INTEGER,
                FOREIGN KEY (branch_id) REFERENCES branches(id)
            );

            CREATE TABLE IF NOT EXISTS commit_files (
                commit_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                PRIMARY KEY (commit_id, file_path),
                FOREIGN KEY (commit_id) REFERENCES commits(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS staging (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_commits_branch ON commits(branch_id);
            CREATE INDEX IF NOT EXISTS idx_commit_files_hash ON commit_files(file_hash);
        """)

        conn.commit()
        conn.close()


def ensure_repo():
    """Check if repository is initialized."""
    if not os.path.exists(VCS_DIR) or not os.path.exists(DB_PATH):
        return False
    return True


def get_config(key, default=None):
    """Get a config value from the database."""
    if not ensure_repo():
        return default
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default


def set_config(key, value):
    """Set a config value in the database."""
    if not ensure_repo():
        return
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        conn.commit()
        conn.close()


def get_current_branch():
    """Get the current branch name."""
    if not ensure_repo():
        return None
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM branches WHERE is_current = 1 LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None


def set_current_branch(name):
    """Switch the current branch."""
    if not ensure_repo():
        return
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE branches SET is_current = 0")
        cursor.execute("UPDATE branches SET is_current = 1 WHERE name = ?", (name,))
        conn.commit()
        conn.close()


def get_branch_commit(branch_name):
    """Get the commit ID for a branch."""
    if not ensure_repo():
        return None
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT commit_id FROM branches WHERE name = ?", (branch_name,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None


def set_branch_commit(branch_name, commit_id):
    """Update the commit ID for a branch."""
    if not ensure_repo():
        return
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE branches SET commit_id = ? WHERE name = ?", (commit_id, branch_name))
        conn.commit()
        conn.close()


def get_commit(commit_id):
    """Get a commit by ID."""
    if not ensure_repo():
        return None
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM commits WHERE id = ?", (commit_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row["id"],
                "message": row["message"],
                "timestamp": row["timestamp"],
                "parent_ids": json.loads(row["parent_ids"]),
                "branch_id": row["branch_id"]
            }
        return None


def get_commit_files(commit_id):
    """Get all files for a commit."""
    if not ensure_repo():
        return {}
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, file_hash FROM commit_files WHERE commit_id = ?", (commit_id,))
        rows = cursor.fetchall()
        conn.close()
        return {row["file_path"]: row["file_hash"] for row in rows}
