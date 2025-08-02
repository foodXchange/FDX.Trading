from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import OperationalError
import time
import os

# Create Base here to avoid circular imports
Base = declarative_base()

# Azure PostgreSQL Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@host:port/database")

# Check if using placeholder values
if "username:password@host:port/database" in DATABASE_URL or not DATABASE_URL or "@:" in DATABASE_URL:
    print("WARNING: Invalid DATABASE_URL - database operations will be limited")
    print("   Please update DATABASE_URL with actual Azure PostgreSQL credentials")
    print(f"   Current DATABASE_URL: {DATABASE_URL}")
    # Create a dummy engine for development
    engine = None
else:
    # Azure PostgreSQL configuration with optimized pooling
    print("Connecting to PostgreSQL database")
    print(f"   Server: {DATABASE_URL.split('@')[1].split(':')[0]}")
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=20,  # Optimized for Azure PostgreSQL
            max_overflow=30,  # Increased for production
            pool_recycle=3600,  # Recycle connections every hour
            pool_timeout=30,  # Connection timeout
            echo=False,  # Disable SQL logging in production
            # Azure PostgreSQL specific optimizations
            connect_args={
                "application_name": "foodxchange_app",
                "options": "-c timezone=utc -c statement_timeout=30000"
            }
        )
        print("PostgreSQL engine created successfully")
    except Exception as e:
        print(f"ERROR: Error creating PostgreSQL engine: {e}")
        engine = None

# Create session maker only if engine exists
if engine is not None:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SessionLocal = None

# Retry logic for DB connection
def verify_database_connection():
    """Verify database connection with retry logic"""
    if engine is None:
        print("WARNING: Database engine not available (using placeholder DATABASE_URL)")
        return False
    
    for i in range(5):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection successful")
            return True
        except OperationalError as e:
            print(f"DB connection failed, retrying ({i+1}/5)... Error: {e}")
            time.sleep(2)
    return False

# Verify connection on module load
if engine is not None and not verify_database_connection():
    print("WARNING: Could not connect to the database. Will retry on first request.")

def get_db():
    """Dependency to get database session"""
    if SessionLocal is None:
        print("WARNING: Database not available - using placeholder configuration")
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 