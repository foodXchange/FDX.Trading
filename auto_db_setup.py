#!/usr/bin/env python3
"""
Automated Database Setup for FoodXchange
This script will test your Azure PostgreSQL connection and set up the database.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time

def test_connection():
    """Test the Azure PostgreSQL connection"""
    print("Testing Azure PostgreSQL connection...")
    print("=" * 50)
    
    # Your Azure PostgreSQL connection details
    DATABASE_URL = "postgresql://pgadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require"
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("[SUCCESS] Connected successfully!")
            print(f"   PostgreSQL version: {version[:50]}...")
            
            # Test database
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"   Connected to database: {db_name}")
            
            # Test user
            result = conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"   Connected as user: {user}")
            
            return True, engine
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return False, None

def check_tables(engine):
    """Check if tables exist"""
    print("\nChecking existing tables...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"[SUCCESS] Found {len(tables)} existing tables:")
                for table in tables:
                    print(f"   - {table}")
                return True
            else:
                print("[WARNING] No tables found - database is empty")
                return False
                
    except Exception as e:
        print(f"[ERROR] Error checking tables: {str(e)}")
        return False

def setup_database(engine):
    """Set up the database with initial tables"""
    print("\nSetting up database...")
    
    # Read the setup script
    setup_script_path = "database/setup_azure_db.sql"
    
    if not os.path.exists(setup_script_path):
        print(f"[ERROR] Setup script not found: {setup_script_path}")
        return False
    
    try:
        with open(setup_script_path, 'r') as f:
            setup_script = f.read()
        
        # Split script into individual statements
        statements = [stmt.strip() for stmt in setup_script.split(';') if stmt.strip()]
        
        with engine.connect() as conn:
            for i, statement in enumerate(statements, 1):
                if statement:
                    print(f"   Executing statement {i}/{len(statements)}...")
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        print(f"   [WARNING] Statement {i} failed (may already exist): {str(e)[:100]}...")
                        conn.rollback()
        
        print("[SUCCESS] Database setup completed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database setup failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("FoodXchange Database Setup")
    print("=" * 50)
    
    # Step 1: Test connection
    success, engine = test_connection()
    if not success:
        print("\n[ERROR] Cannot proceed without database connection.")
        print("Please check:")
        print("1. Your internet connection")
        print("2. Azure firewall settings")
        print("3. Database credentials")
        return
    
    # Step 2: Check existing tables
    has_tables = check_tables(engine)
    
    # Step 3: Setup database if needed
    if not has_tables:
        print("\nDatabase is empty. Setting up tables...")
        setup_success = setup_database(engine)
        if setup_success:
            # Check tables again
            check_tables(engine)
    else:
        print("\n[SUCCESS] Database is already set up!")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Open pgAdmin and connect using the credentials from the setup guide")
    print("2. You should see all your FoodXchange tables")
    print("3. Start your application with: python azure_startup.py")

if __name__ == "__main__":
    main() 