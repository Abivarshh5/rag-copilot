from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.engine import ingest_docs, retrieve_docs

router = APIRouter(prefix="/rag", tags=["RAG"])

class RetrieveRequest(BaseModel):
    query: str
    k: int = 3

@router.post("/ingest")
def ingest_endpoint():
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
