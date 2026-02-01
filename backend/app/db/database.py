import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# SQLite Configuration for Single-Link Deployment
# We prioritize the local app.db which contains the user's credentials.

# Check if running on Hugging Face Spaces
IS_HF_SPACE = os.getenv("SPACE_ID") is not None

_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BASE_DIR = os.path.dirname(_APP_DIR)

if IS_HF_SPACE:
    # Use data directory in the root
    DB_DIR = os.path.join(_BASE_DIR, "data")
    os.makedirs(DB_DIR, exist_ok=True)
    
    DB_FILE = os.path.join(DB_DIR, "app.db")
    DATABASE_URL = f"sqlite:///{DB_FILE}"
    logger.info(f"Using Standardized HF DB Path: {DATABASE_URL}")
else:
    # Local development
    DATABASE_URL = "sqlite:///./app.db"

logger.info(f"Connecting to database: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
