"""
Test Azure PostgreSQL Database Connection
"""
import psycopg2
from sqlalchemy import create_engine, text

# Connection parameters
HOST = "foodxchangepgfr.postgres.database.azure.com"
DATABASE = "foodxchange_db"
USERNAME = "foodxchange_app"
PASSWORD = "Ud30078123"

print("Testing Azure PostgreSQL connection...")
print("=" * 50)

# Test 1: Direct psycopg2 connection
try:
    print("\n1. Testing with psycopg2...")
    conn = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USERNAME,
        password=PASSWORD,
        sslmode='require'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print(f"✓ Connected successfully!")
    print(f"  PostgreSQL version: {record[0][:50]}...")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ psycopg2 connection failed: {str(e)}")

# Test 2: SQLAlchemy connection
try:
    print("\n2. Testing with SQLAlchemy...")
    DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:5432/{DATABASE}?sslmode=require"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"✓ Connected successfully!")
        
        # Check if tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result]
        
        if tables:
            print(f"  Found {len(tables)} tables: {', '.join(tables[:5])}")
            if len(tables) > 5:
                print(f"  ... and {len(tables) - 5} more")
        else:
            print("  No tables found - database is empty")
            
except Exception as e:
    print(f"✗ SQLAlchemy connection failed: {str(e)}")

print("\n" + "=" * 50)
print("\nNext steps:")
print("1. If connection failed - check if user exists or password is correct")
print("2. If connected but no tables - run the database setup script")
print("3. Change the password after setup is complete!")