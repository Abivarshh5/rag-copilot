from app.db.database import engine, Base, IS_HF_SPACE, DB_FILE
from app.db import models
import os
import shutil
import logging

logger = logging.getLogger(__name__)

def init_db():
    if IS_HF_SPACE:
        # Check if target DB exists (persistent or ephemeral)
        if not os.path.exists(DB_FILE):
            logger.info(f"Initializing DB at {DB_FILE}...")
            # Source file (in the deployed repo)
            SOURCE_DB = "app.db" 
            if os.path.exists(SOURCE_DB):
                try:
                    # Ensure destination directory exists
                    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
                    
                    shutil.copy(SOURCE_DB, DB_FILE)
                    
                    # Set permissions (safe default)
                    os.chmod(DB_FILE, 0o666) 
                    
                    logger.info("Database seeded successfully from source.")
                except Exception as e:
                    logger.error(f"Failed to copy database: {e}")
            else:
                logger.warning(f"Source database {SOURCE_DB} not found! Starting with empty DB.")
        else:
            logger.info(f"Database found at {DB_FILE}.")

    Base.metadata.create_all(bind=engine)
    
    # Verify DB content
    try:
        from sqlalchemy.orm import Session
        session = Session(bind=engine)
        user_count = session.query(models.User).count()
        logger.info(f"DB CONFIG CHECK: Found {user_count} users in database.")
        if user_count > 0:
            first_user = session.query(models.User).first()
            logger.info(f"DB CONFIG CHECK: First user email: {first_user.email}")
        session.close()
    except Exception as e:
        logger.error(f"DB CONFIG CHECK FAILED: {e}")
