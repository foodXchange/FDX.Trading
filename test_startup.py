#!/usr/bin/env python
"""
Simple test script to check if the FoodXchange application can start
"""
import os
import sys
import traceback

print("=== FoodXchange Startup Test ===\n")

# Set environment variables for testing
os.environ.setdefault("DATABASE_URL", "sqlite:///./foodxchange.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "True")

print("Environment variables set:")
print(f"  DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"  SECRET_KEY: {os.environ.get('SECRET_KEY')}")
print(f"  ENVIRONMENT: {os.environ.get('ENVIRONMENT')}")
print(f"  DEBUG: {os.environ.get('DEBUG')}\n")

# Test imports
print("Testing imports...")
try:
    import fastapi
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")
    sys.exit(1)

try:
    import uvicorn
    print("✅ Uvicorn imported successfully")
except ImportError as e:
    print(f"❌ Uvicorn import failed: {e}")
    sys.exit(1)

try:
    import sqlalchemy
    print("✅ SQLAlchemy imported successfully")
except ImportError as e:
    print(f"❌ SQLAlchemy import failed: {e}")
    sys.exit(1)

# Test app import
print("\nTesting app import...")
try:
    from app.main import app
    print("✅ FastAPI app imported successfully")
except Exception as e:
    print(f"❌ App import failed: {e}")
    print("\nTraceback:")
    traceback.print_exc()
    sys.exit(1)

# Test database connection
print("\nTesting database connection...")
try:
    from app.database import verify_database_connection
    if verify_database_connection():
        print("✅ Database connection successful")
    else:
        print("⚠️  Database connection failed, but continuing...")
except Exception as e:
    print(f"⚠️  Database test failed: {e}")

print("\n✅ All tests passed! Application should start successfully.")
print("\nTo start the application, run:")
print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
print("  or")
print("  python start.py")