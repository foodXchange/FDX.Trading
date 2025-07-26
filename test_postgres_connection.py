"""
Test Azure PostgreSQL Connection
"""
import os
import sys
from sqlalchemy import create_engine, text

# Load configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.config import get_settings

settings = get_settings()

def test_connection():
    """Test PostgreSQL connection"""
    database_url = settings.database_url
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # Mask password in output
    if '@' in database_url and ':' in database_url:
        password_start = database_url.find(':', database_url.find('://') + 3) + 1
        password_end = database_url.find('@')
        if password_start < password_end:
            password = database_url[password_start:password_end]
            masked_url = database_url.replace(password, '****')
        else:
            masked_url = database_url
    else:
        masked_url = database_url
    print(f"🔍 Testing connection to: {masked_url}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected successfully!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Test database permissions
            conn.execute(text("SELECT 1"))
            print("✅ Can execute queries")
            
            # List existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"📋 Existing tables: {', '.join(tables)}")
            else:
                print("📋 No tables found (database is empty)")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        
        # Provide specific troubleshooting tips
        if "password authentication failed" in str(e):
            print("\n💡 Tip: Check your username and password")
        elif "could not translate host name" in str(e):
            print("\n💡 Tip: Check your server hostname")
        elif "SSL" in str(e):
            print("\n💡 Tip: Try adding ?sslmode=require to the connection string")
        
        return False

def test_create_table():
    """Test creating a table"""
    database_url = settings.database_url
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Try to create a test table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message VARCHAR(255)
                )
            """))
            conn.commit()
            print("✅ Can create tables")
            
            # Insert test data
            conn.execute(text("""
                INSERT INTO connection_test (message) 
                VALUES ('Connection test successful')
            """))
            conn.commit()
            print("✅ Can insert data")
            
            # Read test data
            result = conn.execute(text("SELECT COUNT(*) FROM connection_test"))
            count = result.scalar()
            print(f"✅ Can read data (found {count} test records)")
            
            # Clean up
            conn.execute(text("DROP TABLE connection_test"))
            conn.commit()
            print("✅ Cleanup completed")
            
        return True
        
    except Exception as e:
        print(f"❌ Table operations failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Azure PostgreSQL Connection...\n")
    
    # Test basic connection
    if test_connection():
        print("\n🔧 Testing database operations...\n")
        test_create_table()
        
        print("\n✅ All tests passed! Database is ready for use.")
        print("\n📝 Next steps:")
        print("1. Run database migrations: alembic upgrade head")
        print("2. Start the application: python azure_startup.py")
    else:
        print("\n❌ Connection test failed. Please check your configuration.")
        print("\n📝 Troubleshooting steps:")
        print("1. Verify the DATABASE_URL in your .env file")
        print("2. Check if the server allows connections from your IP")
        print("3. Ensure the database exists and user has permissions")
        print("4. Try the alternative connection string format in .env")