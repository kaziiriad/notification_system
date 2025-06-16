import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from app.core.config import settings

# Initialize settings

if settings.DATABASE_URL is None:
    raise ValueError("DATABASE_URL must be set")


# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    # For PostgreSQL
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,  # Log SQL queries in debug mode
    # For SQLite, uncomment the line below and comment the above lines
    # connect_args={"check_same_thread": False}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Use this in FastAPI endpoints with Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables in the database.
    Call this during application startup.
    """
    # from app.db.sql.models import Base as ModelsBase
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Drop all tables in the database.
    Use with caution - only for development/testing.
    """
    # from app.db.sql.models import Base as ModelsBase
    Base.metadata.drop_all(bind=engine)