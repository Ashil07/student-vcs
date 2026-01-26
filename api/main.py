from fastapi import FastAPI
from pydantic import BaseModel

from core.status import get_status
from core.log import get_log
from core.commit import make_commit
from core.undo import undo_last_commit
from core.exporter import export_repo
from core.importer import import_repo

app = FastAPI(title="Student VCS API")


# ---------- MODELS (for POST requests) ----------

class CommitRequest(BaseModel):
    message: str

class ExportRequest(BaseModel):
    filename: str

class ImportRequest(BaseModel):
    filename: str


# ---------- ROUTES ----------

@app.get("/")
def home():
    return {"message": "Student VCS backend is running"}


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


@app.post("/export")
def export(data: ExportRequest):
    return export_repo(data.filename)


@app.post("/import")
def import_repo_api(data: ImportRequest):
    return import_repo(data.filename)
