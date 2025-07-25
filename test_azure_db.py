"""
Simple Azure Database Connection Test
"""
import os

# First, let's set up the connection string
DATABASE_URL = "postgresql://foodxchange_app:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require"

print("Testing Azure PostgreSQL connection...")
print("=" * 50)

try:
    from sqlalchemy import create_engine, text
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        # Simple connectivity test
        result = conn.execute(text("SELECT 1"))
        print("✓ Connected to Azure PostgreSQL successfully!")
        
        # Check current user
        result = conn.execute(text("SELECT current_user"))
        user = result.fetchone()[0]
        print(f"✓ Connected as user: {user}")
        
        # Check database
        result = conn.execute(text("SELECT current_database()"))
        db = result.fetchone()[0]
        print(f"✓ Connected to database: {db}")
        
        # List tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        
        if tables:
            print(f"\n✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
        else:
            print("\n⚠ No tables found - database is empty")
            print("  You need to run the setup script to create tables")
            
except ImportError:
    print("✗ SQLAlchemy not installed. Install with: pip install sqlalchemy")
except Exception as e:
    print(f"\n✗ Connection failed!")
    print(f"Error: {str(e)}")
    print("\nPossible issues:")
    print("1. The user 'foodxchange_app' might not exist")
    print("2. The password might be incorrect")
    print("3. Network/firewall issues")
    print("\nYou may need to create the user first using the admin account")

print("\n" + "=" * 50)