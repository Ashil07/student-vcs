from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.status import get_status
from core.log import get_log
from core.commit import make_commit
from core.undo import undo_last_commit
from core.exporter import export_repo
from core.importer import import_repo
from core.repo import init_repo
from core.index import add_files
from core.branch import create_branch, list_branches, switch_branch, delete_branch
from core.merge import merge_branch
from core.push_pull import receive_push, serve_pull
from core.supabase_config import is_supabase_enabled

app = FastAPI(title="Student VCS API")

# Mount Supabase routes if configured
if is_supabase_enabled():
    from api import supabase_routes
    app.include_router(supabase_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommitRequest(BaseModel):
    message: str

class ExportRequest(BaseModel):
    filename: str

class ImportRequest(BaseModel):
    filename: str

class BranchRequest(BaseModel):
    name: str

class MergeRequest(BaseModel):
    source: str


@app.get("/")
def home():
    return {"message": "Student VCS backend is running"}


@app.post("/init")
def init():
    return init_repo()


@app.post("/add")
def add():
    return add_files()


@app.get("/status")
def status():
    return get_status()


@app.get("/log")
def log():
    return get_log()


@app.post("/commit")
def commit(data: CommitRequest):
    return make_commit(data.message)


@app.post("/undo")
def undo():
    return undo_last_commit()


@app.get("/branches")
def branches():
    return list_branches()


@app.post("/branches")
def create_new_branch(data: BranchRequest):
    return create_branch(data.name)


@app.post("/switch")
def switch(data: BranchRequest):
    return switch_branch(data.name)


@app.post("/merge")
def merge(data: MergeRequest):
    return merge_branch(data.source)


@app.post("/export")
def export(data: ExportRequest):
    return export_repo(data.filename)


@app.post("/import")
def import_repo_api(data: ImportRequest):
    return import_repo(data.filename)


@app.post("/push/{repo_name}")
async def push(repo_name: str, request: Request):
    body = await request.body()
    return receive_push(body, repo_name)


@app.get("/pull/{repo_name}")
def pull(repo_name: str):
    data = serve_pull(repo_name)
    if data is None:
        return {"success": False, "message": f"Repository '{repo_name}' not found on server"}
    return Response(content=data, media_type="application/octet-stream")
