import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Old database (US East)
old_db_url = os.getenv('DATABASE_URL')

# New database (Poland)
new_db_url = "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/postgres?sslmode=require"

print("Starting database migration from US to Poland...")

try:
    # Connect to old database
    print("Connecting to old database...")
    old_conn = psycopg2.connect(old_db_url)
    old_cur = old_conn.cursor()
    
    # Connect to new database
    print("Connecting to new database in Poland...")
    new_conn = psycopg2.connect(new_db_url)
    new_cur = new_conn.cursor()
    
    # Create foodxchange database
    new_conn.autocommit = True
    try:
        new_cur.execute("CREATE DATABASE foodxchange")
        print("Created foodxchange database")
    except:
        print("Database foodxchange already exists")
    
    # Reconnect to foodxchange database
    new_conn.close()
    new_db_url = "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"
    new_conn = psycopg2.connect(new_db_url)
    new_cur = new_conn.cursor()
    
    # Get table structure from old database
    old_cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = old_cur.fetchall()
    
    print(f"Found {len(tables)} tables to migrate")
    
    # Create tables in new database
    for table in tables:
        table_name = table[0]
        print(f"Migrating table: {table_name}")
        
        # Get CREATE TABLE statement
        old_cur.execute(f"""
            SELECT 
                'CREATE TABLE ' || table_name || ' (' ||
                string_agg(
                    column_name || ' ' || 
                    data_type || 
                    CASE 
                        WHEN character_maximum_length IS NOT NULL 
                        THEN '(' || character_maximum_length || ')'
                        ELSE ''
                    END ||
                    CASE 
                        WHEN is_nullable = 'NO' THEN ' NOT NULL'
                        ELSE ''
                    END,
                    ', '
                ) || ');'
            FROM information_schema.columns
            WHERE table_name = %s
            GROUP BY table_name
        """, (table_name,))
        
        create_statement = old_cur.fetchone()
        if create_statement:
            try:
                new_cur.execute(create_statement[0])
                print(f"  Created table {table_name}")
            except Exception as e:
                print(f"  Table {table_name} already exists or error: {e}")
        
        # Copy data
        old_cur.execute(f"SELECT * FROM {table_name}")
        rows = old_cur.fetchall()
        
        if rows:
            # Get column names
            old_cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = [col[0] for col in old_cur.fetchall()]
            
            # Insert data
            placeholders = ','.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            
            for row in rows:
                try:
                    new_cur.execute(insert_query, row)
                except Exception as e:
                    print(f"  Error inserting row: {e}")
            
            print(f"  Migrated {len(rows)} rows")
    
    # Commit changes
    new_conn.commit()
    
    # Verify migration
    new_cur.execute("SELECT COUNT(*) FROM suppliers")
    count = new_cur.fetchone()[0]
    print(f"\nMigration complete! Suppliers in Poland database: {count:,}")
    
    old_conn.close()
    new_conn.close()
    
except Exception as e:
    print(f"Migration error: {e}")