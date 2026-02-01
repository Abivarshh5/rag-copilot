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

if IS_HF_SPACE:
    # Use persistent storage on HF
    # We copy the deployed app.db to /handler/user/data if it doesn't exist there yet?
    # Actually, the repo ignores changes to /app during runtime? No.
    # On HF, the repo is at /home/user/app. Persistance is at /home/user/data.
    # To keep the credentials we just pushed, we should mistakenly NOT use /data initially?
    # But then we can't write new users.
    # Correct strategy: On startup (init_db), copy ./app.db to /home/user/data/app.db if not exists.
    # But for DATABASE_URL, we point to /home/user/data/app.db
    DB_FILE = "/home/user/data/app.db"
    DATABASE_URL = f"sqlite:///{DB_FILE}"
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
