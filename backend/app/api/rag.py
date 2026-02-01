from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.engine import ingest_docs, retrieve_docs

router = APIRouter(prefix="/rag", tags=["RAG"])

class RetrieveRequest(BaseModel):
    query: str
    k: int = 3

@router.post("/ingest")
def ingest_endpoint():
    # We could capture stdout here but for now let's just use the stats
    stats = ingest_docs()
    return {"status": "success", "stats": stats}

@router.post("/retrieve")
def retrieve_endpoint(request: RetrieveRequest):
    results = retrieve_docs(request.query, request.k)
    return {"results": results}

class AskRequest(BaseModel):
    query: str

@router.post("/ask")
def ask_endpoint(request: AskRequest):
    from app.rag.llm import generate_answer
    result = generate_answer(request.query)
    return result

@router.get("/metrics")
def get_metrics():
    from app.core.metrics import metrics
    return metrics.get_metrics()

@router.get("/debug_count")
def debug_count():
    from app.rag.engine import get_collection
    col = get_collection()
    return {"count": col.count()}

import time
BUILD_TIME = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

@router.get("/debug_path")
def debug_path():
    import os
    from app.rag.engine import DATA_DIR, DOCS_DIR
    res = {
        "build_time": BUILD_TIME,
        "cwd": os.getcwd(),
        "DATA_DIR": DATA_DIR,
        "DOCS_DIR": DOCS_DIR,
        "ls_root": os.listdir("."),
        "exists_data": os.path.exists("data")
    }
    if res["exists_data"]:
        res["ls_data"] = os.listdir("data")
    if os.path.exists(DOCS_DIR):
        res["ls_docs"] = os.listdir(DOCS_DIR)
    return res
