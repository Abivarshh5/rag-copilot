import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db.init_db import init_db
from app.api import auth, rag
from app.rag.engine import init_bm25, DATA_DIR, DOCS_DIR, DB_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for simplicity in production verification/mixed hosting
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

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
    import threading
    
    def run_startup():
        try:
            # 1. Ensure directories exist
            for path in [DATA_DIR, DOCS_DIR, DB_PATH]:
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                    logger.info(f"Created directory: {path}")

            # 2. Initialize DB
            init_db()
            logger.info("Database initialized successfully.")

            # 3. Check if ingestion is needed (self-healing)
            from app.rag.engine import get_collection, ingest_docs, init_bm25
            col = get_collection()
            
            # Initialize BM25 with existing data immediately
            init_bm25()
            
            if col.count() == 0:
                logger.info("Vector DB is empty. Starting background auto-ingestion...")
                stats = ingest_docs()
                logger.info(f"Background auto-ingestion complete: {stats}")
            else:
                logger.info(f"Vector DB already has {col.count()} chunks.")
                
        except Exception as e:
            logger.error(f"Failed during background startup: {e}")

    # Kick off the startup logic in a thread so API becomes ready immediately
    threading.Thread(target=run_startup, daemon=True).start()
    logger.info("Startup sequence initiated in background thread.")

# --- API ROUTES (Define these FIRST) ---
app.include_router(auth.router)
app.include_router(rag.router)

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
        from app.core.security import hash_password, verify_password, create_access_token
        
        results = {}

        # 1. Test raw connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        results["raw_db"] = "ok"
        
        # 2. Test ORM
        db = SessionLocal()
        try:
            test_email = "test_manual@example.com"
            user = db.query(User).filter(User.email == test_email).first()
            results["orm_query"] = "ok"
            results["user_found"] = user is not None
            
            # 3. Test Security Utils (passlib/bcrypt)
            if user:
                pw_ok = verify_password("password123", user.password_hash)
                results["password_verify"] = "ok" if pw_ok else "fail_match"
            else:
                hashed = hash_password("test")
                results["password_hash"] = "ok"
            
            # 4. Test JWT (jose)
            token = create_access_token({"user_id": 1})
            results["jwt_encode"] = "ok"

            return {
                "status": "success", 
                "message": "Full system check complete", 
                "checks": results
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

# --- STATIC FILES & FRONTEND (Define these LAST) ---

# Mount assets first (CSS, JS) so they aren't caught by the catch-all
app.mount("/assets", StaticFiles(directory="app/static/assets"), name="assets")

# Serve index.html for root and client-side routing
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Check if file exists in static (e.g. vite.svg, robots.txt)
    static_file_path = os.path.join("app/static", full_path)
    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    
    # Otherwise return index.html for React Router to handle
    return FileResponse("app/static/index.html")
