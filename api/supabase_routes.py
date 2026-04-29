"""
Supabase-backed API endpoints.
All endpoints require a valid JWT in the Authorization header.
Repos are namespaced per user in PostgreSQL.
"""
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from pydantic import BaseModel
from core.auth import get_current_user
from core import supabase_db as db
from core.supabase_config import is_supabase_enabled

router = APIRouter(prefix="/v2")


def require_supabase():
    if not is_supabase_enabled():
        raise HTTPException(status_code=503, detail="Supabase is not configured. Set USE_SUPABASE=true in .env")


class InitRequest(BaseModel):
    repo_name: str = "default"


class CommitRequest(BaseModel):
    message: str
    repo_name: str = "default"


class BranchRequest(BaseModel):
    name: str
    repo_name: str = "default"


class MergeRequest(BaseModel):
    source: str
    repo_name: str = "default"


class FileInfo(BaseModel):
    file_path: str
    file_hash: str
    repo_name: str = "default"


class ExportRequest(BaseModel):
    filename: str
    repo_name: str = "default"


class ImportRequest(BaseModel):
    filename: str
    repo_name: str = "default"


@router.post("/init")
def init(data: InitRequest, user_id: str = Depends(get_current_user)):
    require_supabase()
    repo_id = db.init_repo(user_id, data.repo_name)
    return {"success": True, "message": f"Repository '{data.repo_name}' initialized", "repo_id": repo_id}


@router.get("/status")
def status(repo_name: str = "default", user_id: str = Depends(get_current_user)):
    require_supabase()
    if not db.ensure_repo(user_id, repo_name):
        return {"success": False, "message": "Not a VCS repository"}

    branch_name = db.get_current_branch(user_id, repo_name)
    commit_id = db.get_branch_commit(user_id, branch_name, repo_name)
    staged = db.get_staging(user_id, repo_name)

    return {
        "success": True,
        "branch": branch_name,
        "commit_id": commit_id,
        "staged": list(staged.keys()),
        "staged_count": len(staged)
    }


@router.post("/stage")
def stage_files(files: list[FileInfo], user_id: str = Depends(get_current_user)):
    require_supabase()
    if not files:
        return {"success": False, "message": "No files provided"}

    repo_name = files[0].repo_name
    db.clear_staging(user_id, repo_name)
    for f in files:
        db.stage_file(user_id, f.file_path, f.file_hash, repo_name)

    return {"success": True, "message": "Files staged", "count": len(files)}


@router.post("/commit")
def commit(data: CommitRequest, user_id: str = Depends(get_current_user)):
    require_supabase()
    import hashlib
    import json
    from datetime import datetime

    if not db.ensure_repo(user_id, data.repo_name):
        return {"success": False, "message": "Not a VCS repository"}

    staged = db.get_staging(user_id, data.repo_name)
    if not staged:
        return {"success": False, "message": "No files staged"}

    branch_name = db.get_current_branch(user_id, data.repo_name)
    parent_id = db.get_branch_commit(user_id, branch_name, data.repo_name)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw = data.message + timestamp + str(parent_id) + branch_name + user_id + data.repo_name
    commit_id = hashlib.sha1(raw.encode()).hexdigest()[:7]

    parent_ids = [parent_id] if parent_id else []
    client = db._client()

    # Get branch_id
    repo_id = db.get_repo_id(user_id, data.repo_name)
    branch_result = client.table("branches").select("id").eq("repo_id", repo_id).eq("name", branch_name).execute()
    branch_id = branch_result.data[0]["id"] if branch_result.data else None

    client.table("commits").insert({
        "id": commit_id,
        "repo_id": repo_id,
        "message": data.message,
        "timestamp": timestamp,
        "parent_ids": json.dumps(parent_ids),
        "branch_id": branch_id
    }).execute()

    for path, file_hash in staged.items():
        client.table("commit_files").insert({
            "commit_id": commit_id,
            "file_path": path,
            "file_hash": file_hash
        }).execute()

    db.clear_staging(user_id, data.repo_name)
    db.set_branch_commit(user_id, branch_name, commit_id, data.repo_name)

    return {
        "success": True,
        "message": "Commit created",
        "commit": {
            "id": commit_id,
            "message": data.message,
            "timestamp": timestamp,
            "branch": branch_name,
            "parent_ids": parent_ids
        }
    }


@router.get("/log")
def log(repo_name: str = "default", user_id: str = Depends(get_current_user)):
    require_supabase()
    commits = db.get_commits(user_id, repo_name)
    return {"success": True, "commits": commits}


@router.get("/branches")
def branches(repo_name: str = "default", user_id: str = Depends(get_current_user)):
    require_supabase()
    data = db.list_branches(user_id, repo_name)
    current = db.get_current_branch(user_id, repo_name)
    return {
        "success": True,
        "branches": [{"name": b["name"], "current": bool(b["is_current"])} for b in data],
        "current": current
    }


@router.post("/branches")
def create_new_branch(data: BranchRequest, user_id: str = Depends(get_current_user)):
    require_supabase()
    result = db.create_branch(user_id, data.name, repo_name=data.repo_name)
    return result


@router.post("/switch")
def switch(data: BranchRequest, user_id: str = Depends(get_current_user)):
    require_supabase()
    db.set_current_branch(user_id, data.name, data.repo_name)
    return {"success": True, "message": f"Switched to branch '{data.name}'"}


@router.post("/merge")
def merge(data: MergeRequest, user_id: str = Depends(get_current_user)):
    require_supabase()
    repo_id = db.get_repo_id(user_id, data.repo_name)
    if not repo_id:
        return {"success": False, "message": "Repository not found"}

    current = db.get_current_branch(user_id, data.repo_name)
    if data.source == current:
        return {"success": False, "message": "Cannot merge a branch into itself"}

    source_commit = db.get_branch_commit(user_id, data.source, data.repo_name)
    target_commit = db.get_branch_commit(user_id, current, data.repo_name)

    if not source_commit:
        return {"success": False, "message": f"Branch '{data.source}' has no commits"}

    if target_commit == source_commit:
        return {"success": True, "message": f"Already up to date with '{data.source}'", "fast_forward": True}

    import hashlib
    import json
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw = f"Merge {data.source} into {current}" + timestamp + str(target_commit) + source_commit + user_id
    commit_id = hashlib.sha1(raw.encode()).hexdigest()[:7]

    parent_ids = []
    if target_commit:
        parent_ids.append(target_commit)
    parent_ids.append(source_commit)

    client = db._client()

    branch_result = client.table("branches").select("id").eq("repo_id", repo_id).eq("name", current).execute()
    branch_id = branch_result.data[0]["id"] if branch_result.data else None

    client.table("commits").insert({
        "id": commit_id,
        "repo_id": repo_id,
        "message": f"Merge branch '{data.source}' into {current}",
        "timestamp": timestamp,
        "parent_ids": json.dumps(parent_ids),
        "branch_id": branch_id
    }).execute()

    # Copy files from both parents (naive merge: source wins)
    target_files = db.get_commit_files(target_commit, user_id, data.repo_name) if target_commit else {}
    source_files = db.get_commit_files(source_commit, user_id, data.repo_name)

    merged = dict(target_files)
    merged.update(source_files)

    for path, file_hash in merged.items():
        client.table("commit_files").insert({
            "commit_id": commit_id,
            "file_path": path,
            "file_hash": file_hash
        }).execute()

    db.set_branch_commit(user_id, current, commit_id, data.repo_name)

    return {
        "success": True,
        "message": f"Merged '{data.source}' into {current}",
        "commit_id": commit_id
    }


@router.post("/undo")
def undo(repo_name: str = "default", user_id: str = Depends(get_current_user)):
    require_supabase()
    current = db.get_current_branch(user_id, repo_name)
    current_commit = db.get_branch_commit(user_id, current, repo_name)

    if not current_commit:
        return {"success": False, "message": "No commits to undo"}

    commit_data = db.get_commit(current_commit, user_id, repo_name)
    if not commit_data:
        return {"success": False, "message": "Commit not found"}

    parent_ids = commit_data.get("parent_ids", [])
    if not parent_ids:
        return {"success": False, "message": "Cannot undo the first commit"}

    parent_id = parent_ids[0]
    client = db._client()
    client.table("commits").delete().eq("id", current_commit).execute()
    db.set_branch_commit(user_id, current, parent_id, repo_name)

    return {"success": True, "message": "Last commit undone", "current_commit": parent_id}
