from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import OperationalError
import time
import os

# Create Base here to avoid circular imports
Base = declarative_base()

# Default to SQLite for development if no DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foodxchange.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        pool_pre_ping=True,
        pool_size=5,  # Smaller pool for SQLite
        max_overflow=10,
        pool_recycle=3600,  # Recycle connections every hour
        pool_timeout=30,  # Connection timeout
    )
else:
    # PostgreSQL/MySQL configuration with optimized pooling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=20,  # Increased for production
        max_overflow=30,  # Increased for production
        pool_recycle=3600,  # Recycle connections every hour
        pool_timeout=30,  # Connection timeout
        echo=False,  # Disable SQL logging in production
        # Additional optimizations for PostgreSQL
        connect_args={
            "application_name": "foodxchange_app",
            "options": "-c timezone=utc"
        } if "postgresql" in DATABASE_URL else {}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Retry logic for DB connection
def verify_database_connection():
    """Verify database connection with retry logic"""
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
if not verify_database_connection():
    print("WARNING: Could not connect to the database. Will retry on first request.")

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 