"""
Simple Azure PostgreSQL Connection Test
"""
import os
from sqlalchemy import create_engine, text

# Hardcode the connection string from .env
DATABASE_URL = "postgresql://foodxchangedbadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange?sslmode=require"

def test_connection():
    """Test PostgreSQL connection"""
    
    # Mask password in output
    masked_url = DATABASE_URL.replace("Ud30078123", "****")
    print(f"Testing connection to: {masked_url}")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("Connected successfully!")
            print(f"PostgreSQL version: {version}")
            
            # Test database permissions
            conn.execute(text("SELECT 1"))
            print("Can execute queries")
            
            # List existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"Existing tables: {', '.join(tables)}")
            else:
                print("No tables found (database is empty)")
            
        return True
        
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        
        # Try alternative format
        if "foodxchangedbadmin" in DATABASE_URL:
            print("\nTrying alternative connection format...")
            alt_url = "postgresql://foodxchangedbadmin%40foodxchangepgfr:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange?sslmode=require"
            try:
                engine = create_engine(alt_url)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    print("Alternative format works! Update your .env file with this format.")
                    return True
            except Exception as e2:
                print(f"Alternative format also failed: {str(e2)}")
        
        return False

if __name__ == "__main__":
    print("Testing Azure PostgreSQL Connection...\n")
    
    if test_connection():
        print("\nConnection successful! Database is ready.")
    else:
        print("\nConnection failed. Please check:")
        print("1. Server firewall rules allow your IP")
        print("2. Username and password are correct")
        print("3. Database 'foodxchange' exists")