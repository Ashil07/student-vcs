"""
Supabase Storage integration for blob objects.
Provides an alternative to local .myvcs/objects/ directory.
"""
import hashlib
from core.supabase_config import get_supabase_client, is_supabase_enabled

BUCKET_NAME = "vcs-objects"


def _ensure_bucket():
    client = get_supabase_client()
    try:
        client.storage.get_bucket(BUCKET_NAME)
    except Exception:
        client.storage.create_bucket(BUCKET_NAME, options={"public": False})


def upload_blob(data: bytes, file_hash: str, user_id: str) -> dict:
    """Upload a blob object to Supabase Storage."""
    if not is_supabase_enabled():
        return {"success": False, "message": "Supabase not configured"}

    _ensure_bucket()
    client = get_supabase_client()
    path = f"{user_id}/{file_hash}"

    try:
        client.storage.from_(BUCKET_NAME).upload(path, data, {"content-type": "application/octet-stream"})
        return {"success": True, "path": path}
    except Exception as e:
        if "already exists" in str(e).lower():
            return {"success": True, "path": path}
        return {"success": False, "message": str(e)}


def download_blob(file_hash: str, user_id: str) -> bytes:
    """Download a blob object from Supabase Storage."""
    if not is_supabase_enabled():
        return b""

    client = get_supabase_client()
    path = f"{user_id}/{file_hash}"

    try:
        return client.storage.from_(BUCKET_NAME).download(path)
    except Exception:
        return b""


def hash_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()
