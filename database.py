from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Print environment for debugging (without exposing credentials)
logger.info("Environment variables for database connection:")
if "DATABASE_URL" in os.environ:
    logger.info("DATABASE_URL environment variable is set")
else:
    logger.info("DATABASE_URL not found in environment")

# For Railway deployment - use environment variable or fallback safely
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///./app.db"

logger.info(f"Final database URL type: {'PostgreSQL' if 'postgresql' in SQLALCHEMY_DATABASE_URL else 'SQLite'}")

# Configure engine based on database type
if 'sqlite' in SQLALCHEMY_DATABASE_URL:
    logger.info("Using SQLite configuration")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    logger.info("Using PostgreSQL configuration")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
    )
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()