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

# Check if running on Hugging Face Spaces
IS_HF_SPACE = os.getenv("SPACE_ID") is not None

if IS_HF_SPACE:
    # User does NOT have persistent storage enabled (/data).
    # We must use a local writable directory inside the container.
    # standard HF working dir is /home/user/app.
    # We can write to a subdirectory like /home/user/app/data or just ./data
    # BUT we need to make sure we copy the seeded db there.
    
    # Force use of local directory
    DB_DIR = os.path.join(os.getcwd(), "data")
    os.makedirs(DB_DIR, exist_ok=True)
    
    DB_FILE = os.path.join(DB_DIR, "app.db")
    DATABASE_URL = f"sqlite:///{DB_FILE}"
    logger.info(f"Using Ephemeral DB Path: {DATABASE_URL}")
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
