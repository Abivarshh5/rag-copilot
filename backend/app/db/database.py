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
    f"postgresql+psycopg2://postgres:{SUPABASE_PASSWORD}@db.tljppxeshzeyjrupxpcc.supabase.co:5432/postgres"
)

logger.info(f"Connecting to database...")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
