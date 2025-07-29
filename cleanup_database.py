#!/usr/bin/env python3
"""
Database cleanup script - Keep only AI product analysis tables
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Tables to keep for AI product analysis
TABLES_TO_KEEP = {
    'product_analyses',
    'product_briefs', 
    'product_images',
    'ai_insights',
    'users',  # Keep users table for authentication
    'alembic_version'  # Keep for migrations tracking
}

def cleanup_database():
    """Clean up database, keeping only AI-related tables"""
    # Get database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///./foodxchange.db")
    
    print(f"Connecting to database: {database_url.split('@')[0]}...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Get inspector to list tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"\nFound {len(existing_tables)} tables in database:")
        for table in existing_tables:
            print(f"  - {table}")
        
        # Find tables to drop
        tables_to_drop = [t for t in existing_tables if t not in TABLES_TO_KEEP]
        
        if not tables_to_drop:
            print("\nNo tables to drop. Database already clean!")
            return
        
        print(f"\nTables to drop ({len(tables_to_drop)}):")
        for table in tables_to_drop:
            print(f"  - {table}")
        
        # Confirm deletion
        response = input("\nAre you sure you want to drop these tables? (yes/no): ")
        if response.lower() != 'yes':
            print("Cleanup cancelled.")
            return
        
        # Drop tables
        with engine.connect() as conn:
            for table in tables_to_drop:
                try:
                    # Use CASCADE to handle foreign key constraints
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    conn.commit()
                    print(f"  ✓ Dropped table: {table}")
                except Exception as e:
                    print(f"  ✗ Error dropping {table}: {e}")
        
        # List remaining tables
        print("\nRemaining tables:")
        inspector = inspect(engine)
        remaining_tables = inspector.get_table_names()
        for table in remaining_tables:
            print(f"  - {table}")
        
        print("\nDatabase cleanup complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cleanup_database()