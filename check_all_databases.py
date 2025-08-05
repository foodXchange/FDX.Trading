import psycopg2
import os
from dotenv import load_dotenv
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

try:
    # Connect using environment variable
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("🔍 Checking all databases and tables...\n")
    
    # Get current database
    cur.execute("SELECT current_database()")
    current_db = cur.fetchone()[0]
    print(f"📍 Current database: {current_db}")
    
    # List all databases
    cur.execute("""
        SELECT datname 
        FROM pg_database 
        WHERE datistemplate = false
        ORDER BY datname
    """)
    print("\n📚 All databases:")
    for db in cur.fetchall():
        print(f"   - {db[0]}")
    
    # List all tables in current database
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    print(f"\n📋 Tables in '{current_db}':")
    for table in tables:
        # Get row count for each table
        cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cur.fetchone()[0]
        print(f"   - {table[0]}: {count:,} rows")
    
    # Check for other schemas
    cur.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
    """)
    schemas = cur.fetchall()
    print("\n📁 Schemas:")
    for schema in schemas:
        print(f"   - {schema[0]}")
    
    # Check if there's another suppliers table
    cur.execute("""
        SELECT 
            schemaname,
            tablename,
            n_live_tup as estimated_rows
        FROM pg_stat_user_tables
        WHERE tablename LIKE '%supplier%'
        ORDER BY n_live_tup DESC
    """)
    supplier_tables = cur.fetchall()
    print("\n🔎 Tables with 'supplier' in name:")
    for schema, table, rows in supplier_tables:
        print(f"   - {schema}.{table}: ~{rows:,} rows")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")