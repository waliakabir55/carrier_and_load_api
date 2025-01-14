from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings
from sqlalchemy.ext.declarative import declarative_base
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=True  # Set to True for SQL logging
)

logger.info(f"Database URL: {settings.DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger.info("Database sessionmaker created")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()
logger.info("Base declarative_base created")