#!/usr/bin/env python3
"""
Local FoodXchange Startup Script
This script sets up the environment and starts the application locally.
"""

import os
import sys
from sqlalchemy import create_engine, text

# Set the database URL for Azure PostgreSQL
os.environ["DATABASE_URL"] = "postgresql://pgadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require"

def test_database():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        engine = create_engine(os.environ["DATABASE_URL"])
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def start_application():
    """Start the FastAPI application"""
    print("\n🚀 Starting FoodXchange application...")
    
    try:
        # Import and start the application
        from app.main import app
        import uvicorn
        
        print("✅ Application loaded successfully!")
        print("\n🌐 Access your application at:")
        print("   http://localhost:8000")
        print("\n📚 API Documentation at:")
        print("   http://localhost:8000/docs")
        print("\n🔄 Press Ctrl+C to stop the server")
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Please install missing dependencies:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")

def main():
    """Main function"""
    print("=" * 50)
    print("🚀 FoodXchange Local Startup")
    print("=" * 50)
    
    # Test database connection
    if not test_database():
        print("\n❌ Cannot start without database connection.")
        return
    
    # Start application
    start_application()

if __name__ == "__main__":
    main() 