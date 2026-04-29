"""
Supabase PostgreSQL database layer.
Mirrors the SQLite layer in db.py but uses Supabase for cloud persistence.
All operations are scoped to (user_id, repo_id).
"""
import json
from core.supabase_config import get_supabase_client


def _client():
    return get_supabase_client()


def get_or_create_repo(user_id: str, repo_name: str = "default"):
    """Get repo ID for user, creating if needed."""
    client = _client()
    result = client.table("repos").select("id").eq("user_id", user_id).eq("name", repo_name).execute()
    if result.data:
        return result.data[0]["id"]

    insert = client.table("repos").insert({
        "user_id": user_id,
        "name": repo_name
    }).execute()
    return insert.data[0]["id"]


def ensure_repo(user_id: str, repo_name: str = "default"):
    """Check if a repository exists for this user."""
    client = _client()
    result = client.table("repos").select("id").eq("user_id", user_id).eq("name", repo_name).execute()
    return len(result.data) > 0


def init_repo(user_id: str, repo_name: str = "default"):
    """Initialize a new repo for a user (creates 'main' branch)."""
    client = _client()
    repo_id = get_or_create_repo(user_id, repo_name)

    # Check if main branch exists
    result = client.table("branches").select("id").eq("repo_id", repo_id).eq("name", "main").execute()
    if not result.data:
        client.table("branches").insert({
            "repo_id": repo_id,
            "name": "main",
            "commit_id": None,
            "is_current": 1
        }).execute()
    return repo_id


def get_repo_id(user_id: str, repo_name: str = "default"):
    client = _client()
    result = client.table("repos").select("id").eq("user_id", user_id).eq("name", repo_name).execute()
    if result.data:
        return result.data[0]["id"]
    return None


def get_current_branch(user_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return None
    client = _client()
    result = client.table("branches").select("name").eq("repo_id", repo_id).eq("is_current", 1).limit(1).execute()
    if result.data:
        return result.data[0]["name"]
    return None


def set_current_branch(user_id: str, name: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return
    client = _client()
    client.table("branches").update({"is_current": 0}).eq("repo_id", repo_id).execute()
    client.table("branches").update({"is_current": 1}).eq("repo_id", repo_id).eq("name", name).execute()


def get_branch_commit(user_id: str, branch_name: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return None
    client = _client()
    result = client.table("branches").select("commit_id").eq("repo_id", repo_id).eq("name", branch_name).execute()
    if result.data:
        return result.data[0]["commit_id"]
    return None


def set_branch_commit(user_id: str, branch_name: str, commit_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return
    client = _client()
    client.table("branches").update({"commit_id": commit_id}).eq("repo_id", repo_id).eq("name", branch_name).execute()


def get_commit(commit_id: str, user_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return None
    client = _client()
    result = client.table("commits").select("*").eq("id", commit_id).eq("repo_id", repo_id).limit(1).execute()
    if result.data:
        row = result.data[0]
        return {
            "id": row["id"],
            "message": row["message"],
            "timestamp": str(row["timestamp"]),
            "parent_ids": row["parent_ids"] if isinstance(row["parent_ids"], list) else json.loads(row["parent_ids"]),
            "branch_id": row["branch_id"]
        }
    return None


def get_commit_files(commit_id: str, user_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return {}
    client = _client()
    result = client.table("commit_files").select("file_path,file_hash").eq("commit_id", commit_id).execute()
    return {row["file_path"]: row["file_hash"] for row in result.data}


def list_branches(user_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return []
    client = _client()
    result = client.table("branches").select("name,is_current").eq("repo_id", repo_id).order("name").execute()
    return result.data


def create_branch(user_id: str, name: str, from_commit: str = None, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        repo_id = init_repo(user_id, repo_name)

    client = _client()
    # Check if exists
    existing = client.table("branches").select("id").eq("repo_id", repo_id).eq("name", name).execute()
    if existing.data:
        return {"success": False, "message": f"Branch '{name}' already exists"}

    client.table("branches").insert({
        "repo_id": repo_id,
        "name": name,
        "commit_id": from_commit,
        "is_current": 0
    }).execute()
    return {"success": True, "message": f"Branch '{name}' created"}


def get_staging(user_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return {}
    client = _client()
    result = client.table("staging").select("file_path,file_hash").eq("repo_id", repo_id).execute()
    return {row["file_path"]: row["file_hash"] for row in result.data}


def clear_staging(user_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return
    client = _client()
    client.table("staging").delete().eq("repo_id", repo_id).execute()


def stage_file(user_id: str, file_path: str, file_hash: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return
    client = _client()
    client.table("staging").upsert({
        "repo_id": repo_id,
        "file_path": file_path,
        "file_hash": file_hash
    }).execute()


def get_commits(user_id: str, repo_name: str = "default"):
    repo_id = get_repo_id(user_id, repo_name)
    if not repo_id:
        return []
    client = _client()
    result = client.table("commits").select("*").eq("repo_id", repo_id).order("timestamp", desc=True).execute()
    commits = []
    for row in result.data:
        commits.append({
            "id": row["id"],
            "message": row["message"],
            "timestamp": str(row["timestamp"]),
            "parent_ids": row["parent_ids"] if isinstance(row["parent_ids"], list) else json.loads(row["parent_ids"]),
            "branch_id": row["branch_id"]
        })
    return commits
