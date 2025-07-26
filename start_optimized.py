#!/usr/bin/env python3
"""
FoodXchange Optimized Startup Script
Sets up environment variables and starts the application with the optimized schema
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 50)
    print("🚀 FoodXchange Optimized Startup")
    print("=" * 50)
    
    # Set environment variables for Supabase
    os.environ["DATABASE_URL"] = "postgresql://postgres:Ud30078123@db.hlugyivdpcwzivhvgjii.supabase.co:5432/postgres?sslmode=require"
    os.environ["SUPABASE_URL"] = "https://hlugyivdpcwzivhvgjii.supabase.co"
    os.environ["SUPABASE_ANON_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhsdWd5aXZkcGN3emlodmhnamppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MDkxMTIsImV4cCI6MjA2OTA4NTExMn0._UEtBBPKcR9CIWzKaeUp_uvhxN3S9-4PTgB2BUtZLPY"
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhsdWd5aXZkcGN3emlodmhnamppIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzUwOTExMiwiZXhwIjoyMDY5MDg1MTEyfQ.1IDT2jatU2PAc6TOfox9UZpn6IdD4RTeaWY99n7mLzo"
    
    # Set other required environment variables
    os.environ["SECRET_KEY"] = "your-secret-key-here-change-this-in-production"
    os.environ["ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["EMAILS_ENABLED"] = "false"
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
    os.environ["AZURE_STORAGE_ENABLED"] = "false"
    
    print("🔍 Testing database connection...")
    
    try:
        # Test database connection
        import psycopg2
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Please make sure:")
        print("1. Your Supabase database is running")
        print("2. The optimized schema has been applied")
        print("3. Your credentials are correct")
        return
    
    print("🚀 Starting FoodXchange application...")
    print("📱 Access your app at: http://localhost:8000")
    print("📊 API docs at: http://localhost:8000/docs")
    print("=" * 50)
    
    # Start the application
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

if __name__ == "__main__":
    main() 