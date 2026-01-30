import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Supabase PostgreSQL connection
# Password is URL-encoded to handle special characters like @
SUPABASE_PASSWORD = quote_plus("Varshini@512")
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql+psycopg2://postgres.tljppxeshzeyjrupxpcc:{SUPABASE_PASSWORD}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
)

logger.info(f"Connecting to database...")

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    # Supabase Transaction Mode Pooler requirements:
    # 1. Disable prepared statements (prepare_threshold=None)
    # 2. Add keepalives to prevent timeouts
    connect_args={
        "prepare_threshold": None,
        "keepalives": 1, 
        "keepalives_idle": 30,
        "keepalives_interval": 10, 
        "keepalives_count": 5
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
