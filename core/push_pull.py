import json
import os
import sqlite3
import tempfile
import shutil
from core.db import get_db, ensure_repo
from core.exporter import export_repo
from core.importer import import_repo


def push_repo(remote_url, repo_name="local"):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    try:
        import urllib.request
        import urllib.parse

        tmp_path = f"{repo_name}.vcs"
        export_repo(tmp_path)

        with open(tmp_path, "rb") as f:
            data = f.read()

        req = urllib.request.Request(
            f"{remote_url}/push/{repo_name}",
            data=data,
            method="POST",
            headers={"Content-Type": "application/octet-stream"}
        )

        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode())

        os.remove(tmp_path)
        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"Push failed: {str(e)}"
        }


def pull_repo(remote_url, repo_name="local"):
    if not ensure_repo():
        return {
            "success": False,
            "message": "Not a VCS repository"
        }

    try:
        import urllib.request

        req = urllib.request.Request(
            f"{remote_url}/pull/{repo_name}",
            method="GET"
        )

        response = urllib.request.urlopen(req, timeout=30)
        data = response.read()

        tmp_path = f"{repo_name}_pulled.vcs"
        with open(tmp_path, "wb") as f:
            f.write(data)

        result = import_repo(tmp_path)
        os.remove(tmp_path)
        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"Pull failed: {str(e)}"
        }


def receive_push(data, repo_name="local"):
    """Server-side: receive a pushed repository."""
    try:
        tmp_path = f"{repo_name}.vcs"
        with open(tmp_path, "wb") as f:
            f.write(data)

        extract_dir = f"remotes/{repo_name}"
        os.makedirs(extract_dir, exist_ok=True)

        import zipfile
        with zipfile.ZipFile(tmp_path, "r") as zf:
            zf.extractall(extract_dir)

        os.remove(tmp_path)

        return {
            "success": True,
            "message": f"Repository '{repo_name}' received successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Receive failed: {str(e)}"
        }


def serve_pull(repo_name="local"):
    """Server-side: prepare a repository for pulling."""
    extract_dir = f"remotes/{repo_name}"
    repo_path = os.path.join(extract_dir, "repo", ".myvcs")

    if not os.path.exists(repo_path):
        return None

    tmp_path = f"{repo_name}_serve.vcs"
    import zipfile
    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(extract_dir):
            for name in files:
                full_path = os.path.join(root, name)
                arc_name = os.path.relpath(full_path, extract_dir)
                zf.write(full_path, arc_name)

    with open(tmp_path, "rb") as f:
        data = f.read()

    os.remove(tmp_path)
    return data
