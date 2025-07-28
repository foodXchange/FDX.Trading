from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
import time
import os

# Import Base from models to re-export it
from app.models.base import Base

# Default to SQLite for development if no DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foodxchange.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    # PostgreSQL/MySQL configuration with pooling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
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