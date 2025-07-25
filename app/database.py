from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from app.config import get_settings
import time

settings = get_settings()

DATABASE_URL = settings.database_url

# Engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Retry logic for DB connection
for i in range(5):
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        break
    except OperationalError:
        print(f"DB connection failed, retrying ({i+1}/5)...")
        time.sleep(2)
else:
    raise RuntimeError("Could not connect to the database after 5 attempts.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 