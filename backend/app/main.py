import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import init_db
from app.api import auth, rag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Middleware - permit all origins for now to resolve Vercel deployment issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://rag-copilot.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=False, # Must be False if using ["*"] or combined with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = (time.time() - start_time) * 1000  # Convert to ms
    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code} - Latency: {latency:.2f}ms"
    )
    return response

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {
        "message": "RAG Copilot Backend is running!",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(rag.router)
