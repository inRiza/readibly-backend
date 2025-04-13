from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Base and model classes
from database import Base
from models.user import User  # Make sure this exists and is imported

def test_connection():
    try:
        # Direct connection to PostgreSQL
        db_url = "postgresql://postgres:zxJItkJsMcEdKVXSLkxvtHWPHKFskORL@ballast.proxy.rlwy.net:46603/railway"
        logger.info(f"Attempting to connect to: {db_url[:20]}...")
        
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        logger.info("Testing connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Connection successful. Result: {result.fetchone()}")
        
        # Create tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        
        # Check which tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {tables}")
        
        # Check user table structure
        if 'users' in tables:
            columns = [col['name'] for col in inspector.get_columns('users')]
            logger.info(f"Columns in users table: {columns}")
        else:
            logger.info("Users table was not created")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)