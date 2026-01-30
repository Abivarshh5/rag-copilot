import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

# Determine if running on Hugging Face Spaces
IS_HF_SPACE = os.getenv("SPACE_ID") is not None

# Use /home/user/data for HF Spaces persistent storage (recommended by HF)
# Falls back to local path for development
if IS_HF_SPACE:
    DB_DIR = "/home/user/data"
    DB_FILE = os.path.join(DB_DIR, "app.db")
else:
    # Local development
    DB_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_FILE = os.path.join(DB_DIR, "app.db")

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Get DATABASE_URL from environment or use SQLite
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

logger.info(f"Database path: {DATABASE_URL}")
logger.info(f"Running on HF Spaces: {IS_HF_SPACE}")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
