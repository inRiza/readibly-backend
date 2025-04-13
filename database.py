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

# Debug environment variables
logger.info(f"Environment variables after load_dotenv: DATABASE_URL exists: {'DATABASE_URL' in os.environ}")
if 'DATABASE_URL' in os.environ:
    logger.info(f"DATABASE_URL from environment: {os.environ['DATABASE_URL'][:20]}...")
else:
    logger.info("DATABASE_URL not found in environment variables")

# Prioritize environment variables, with fallback to SQLite
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///./app.db"
logger.info(f"Using database URL: {SQLALCHEMY_DATABASE_URL[:20]}...")

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