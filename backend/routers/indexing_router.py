"""Stage 1: Indexing endpoints"""

import os
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from pydantic import BaseModel

from config import settings
from dependencies import get_indexing_pipeline, get_vector_store

router = APIRouter(prefix="/indexing", tags=["Indexing"])

# Track background indexing jobs
_indexing_status = {"status": "idle", "progress": None, "last_result": None}


class IndexDirRequest(BaseModel):
    directory: Optional[str] = None  # defaults to raw_pptx_path from config


class CrawlRequest(BaseModel):
    url: str
    course_name: str
    cookies: Optional[dict] = None


def _run_indexing(directory: str):
    global _indexing_status
    _indexing_status["status"] = "running"
    try:
        pipeline = get_indexing_pipeline()
        result = pipeline.index_directory(directory)
        _indexing_status["status"] = "done"
        _indexing_status["last_result"] = result
    except Exception as e:
        _indexing_status["status"] = "error"
        _indexing_status["last_result"] = {"error": str(e)}


@router.post("/index-directory")
async def index_directory(request: IndexDirRequest, background_tasks: BackgroundTasks):
    """Index all PPTX files in a directory (runs in background)."""
    directory = request.directory or settings.raw_pptx_path
    if not os.path.isdir(directory):
        raise HTTPException(status_code=404, detail=f"Directory not found: {directory}")

    global _indexing_status
    if _indexing_status["status"] == "running":
        raise HTTPException(status_code=409, detail="Indexing already in progress")

    _indexing_status = {"status": "queued", "progress": None, "last_result": None}
    background_tasks.add_task(_run_indexing, directory)
    return {"status": "queued", "directory": directory}


@router.post("/index-file")
async def index_file(file: UploadFile = File(...)):
    """Upload and index a single PPTX file."""
    import tempfile, shutil
    if not file.filename.endswith((".pptx", ".ppt")):
        raise HTTPException(status_code=400, detail="Only .pptx/.ppt files accepted")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        pipeline = get_indexing_pipeline()
        result = pipeline.index_file(tmp_path)
        return {"status": "done", "filename": file.filename, **result}
    finally:
        os.unlink(tmp_path)


@router.post("/reset")
async def reset_index():
    """Delete all indexed vectors and start fresh."""
    vs = get_vector_store()
    vs.reset()
    return {"status": "reset", "message": "Vector store cleared"}


@router.get("/status")
async def indexing_status():
    """Get current indexing status and vector store stats."""
    vs = get_vector_store()
    stats = vs.get_stats()
    return {**_indexing_status, **stats}


# --- Legacy stub endpoints kept for API compatibility ---

@router.post("/crawl")
async def crawl_documents(request: CrawlRequest):
    return {"status": "not_implemented", "message": "Crawling endpoint – provide URL + cookies"}


@router.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    return {"status": "not_implemented", "filename": file.filename}
