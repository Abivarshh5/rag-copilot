import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import init_db
from app.api import auth, rag
from app.rag.engine import init_bm25, DATA_DIR, DOCS_DIR, DB_PATH

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
    try:
        # 1. Ensure directories exist for HF write access
        for path in [DATA_DIR, DOCS_DIR, DB_PATH]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                logger.info(f"Created directory: {path}")

        # 2. Initialize DB
        init_db()
        logger.info("Database initialized successfully.")

        # 3. Initialize BM25
        init_bm25()
        logger.info("BM25 initialized successfully.")
    except Exception as e:
        logger.error(f"Failed during startup: {e}")

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

@app.get("/debug_db")
def debug_db():
    try:
        from sqlalchemy import text
        from sqlalchemy.orm import Session
        from app.db.database import engine, SessionLocal
        from app.db.models import User
        
        # 1. Test raw connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        # 2. Test ORM
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            return {
                "status": "success", 
                "message": "Database and ORM connected", 
                "user_count": user_count
            }
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "message": str(e), 
            "type": str(type(e)),
            "traceback": traceback.format_exc()
        }

app.include_router(auth.router)
app.include_router(rag.router)
