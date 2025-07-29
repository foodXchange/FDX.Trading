#!/usr/bin/env python3
"""
List all tables in the database
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
import getpass

load_dotenv()

print("Database Table Inspector")
print("=" * 50)

# Get database URL
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL not set in .env file")
    sys.exit(1)

# Parse and display connection info
if "@" in database_url:
    parts = database_url.split("@")
    print(f"Database: {parts[1].split('/')[1] if len(parts[1].split('/')) > 1 else 'unknown'}")
    print(f"Host: {parts[1].split('/')[0]}")

# If it's localhost PostgreSQL, ask for password
if "localhost:5432" in database_url and "password" in database_url:
    print("\nLocal PostgreSQL detected. Enter the correct password:")
    password = getpass.getpass("PostgreSQL password: ")
    database_url = database_url.replace(":password@", f":{password}@")

try:
    print("\nConnecting to database...")
    engine = create_engine(database_url)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"Connected! PostgreSQL version: {version[:50]}...")
    
    # Get all tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\nFound {len(tables)} tables:")
    print("-" * 50)
    
    for table in sorted(tables):
        # Get row count for each table
        try:
            with engine.connect() as conn:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"{table:<30} {count:>10} rows")
        except:
            print(f"{table:<30}      Error reading")
    
    print("-" * 50)
    print("\nTo clean up the database (keep only AI tables), run:")
    print("  python cleanup_database.py")
    
except Exception as e:
    print(f"\nERROR: Could not connect to database")
    print(f"Details: {e}")
    print("\nPlease check your DATABASE_URL in .env file")