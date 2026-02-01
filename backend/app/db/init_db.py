from app.db.database import engine, Base, IS_HF_SPACE, DB_FILE
from app.db import models
import os
import shutil
import logging

logger = logging.getLogger(__name__)

def init_db():
    if IS_HF_SPACE:
        # Check if persistent DB exists
        if not os.path.exists(DB_FILE):
            logger.info(f"First run on HF detected. Copying seeded app.db to {DB_FILE}...")
            # Source file (in the deployed repo)
            # Assuming working dir is /home/user/app, app.db should be in root
            SOURCE_DB = "app.db" 
            if os.path.exists(SOURCE_DB):
                try:
                    shutil.copy(SOURCE_DB, DB_FILE)
                    logger.info("Database copied successfully.")
                except Exception as e:
                    logger.error(f"Failed to copy database: {e}")
            else:
                logger.warning(f"Source database {SOURCE_DB} not found! Starting with empty DB.")
        else:
            logger.info("Persistent database found.")

    Base.metadata.create_all(bind=engine)
