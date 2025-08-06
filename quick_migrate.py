import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Source database (US East)
source_db = os.getenv('DATABASE_URL')

# Target database (Poland)
target_db = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/postgres?sslmode=require"

print("=" * 60)
print("DATABASE MIGRATION: US EAST -> POLAND CENTRAL")
print("=" * 60)

try:
    # Connect to target DB to create database
    print("\n1. Creating foodxchange database in Poland...")
    conn = psycopg2.connect(target_db)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        cur.execute("CREATE DATABASE foodxchange")
        print("   [OK] Database 'foodxchange' created")
    except psycopg2.errors.DuplicateDatabase:
        print("   [OK] Database 'foodxchange' already exists")
    
    cur.close()
    conn.close()
    
    # Now connect to the foodxchange database
    target_db = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"
    
    print("\n2. Connecting to source database (US East)...")
    source_conn = psycopg2.connect(source_db)
    source_cur = source_conn.cursor()
    print("   [OK] Connected to source database")
    
    print("\n3. Connecting to target database (Poland)...")
    target_conn = psycopg2.connect(target_db)
    target_cur = target_conn.cursor()
    print("   [OK] Connected to target database")
    
    # Create suppliers table
    print("\n4. Creating suppliers table...")
    target_cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id SERIAL PRIMARY KEY,
            supplier_name TEXT,
            company_name TEXT,
            company_email TEXT,
            company_website TEXT,
            country TEXT,
            products TEXT,
            product_categories TEXT,
            supplier_type TEXT,
            certifications TEXT,
            rating DECIMAL,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    target_conn.commit()
    print("   [OK] Suppliers table created")
    
    # Check if table already has data
    target_cur.execute("SELECT COUNT(*) FROM suppliers")
    existing_count = target_cur.fetchone()[0]
    
    if existing_count > 0:
        print(f"\n   ⚠ Target already has {existing_count} suppliers. Skipping data migration.")
    else:
        # Copy suppliers data
        print("\n5. Copying suppliers data...")
        source_cur.execute("SELECT * FROM suppliers ORDER BY id")
        
        # Get column names
        columns = [desc[0] for desc in source_cur.description]
        
        # Batch insert
        batch_size = 1000
        total = 0
        
        while True:
            rows = source_cur.fetchmany(batch_size)
            if not rows:
                break
            
            # Create insert query
            placeholders = ','.join(['%s'] * len(columns))
            insert_query = f"""
                INSERT INTO suppliers ({','.join(columns)}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO NOTHING
            """
            
            for row in rows:
                try:
                    target_cur.execute(insert_query, row)
                except Exception as e:
                    print(f"   Error inserting row: {e}")
            
            target_conn.commit()
            total += len(rows)
            print(f"   Migrated {total} suppliers...")
        
        print(f"   [OK] Total suppliers migrated: {total}")
    
    # Create other tables if they exist
    print("\n6. Creating additional tables...")
    
    # supplier_search_keywords table
    target_cur.execute("""
        CREATE TABLE IF NOT EXISTS supplier_search_keywords (
            id SERIAL PRIMARY KEY,
            supplier_id INTEGER,
            keyword TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for performance
    print("\n7. Creating indexes...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_suppliers_country ON suppliers(country)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_products ON suppliers(products)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(supplier_name)",
    ]
    
    for idx in indexes:
        target_cur.execute(idx)
        print(f"   [OK] Created index")
    
    target_conn.commit()
    
    # Verify migration
    print("\n8. Verifying migration...")
    target_cur.execute("SELECT COUNT(*) FROM suppliers")
    final_count = target_cur.fetchone()[0]
    
    target_cur.execute("SELECT COUNT(*) FROM suppliers WHERE products IS NOT NULL AND LENGTH(products) > 100")
    enhanced_count = target_cur.fetchone()[0]
    
    print(f"   [OK] Total suppliers in Poland: {final_count:,}")
    print(f"   [OK] Enhanced suppliers: {enhanced_count:,}")
    
    # Sample data
    target_cur.execute("SELECT supplier_name, country FROM suppliers LIMIT 3")
    samples = target_cur.fetchall()
    print("\n   Sample migrated data:")
    for s in samples:
        print(f"   - {s[0]} ({s[1]})")
    
    source_conn.close()
    target_conn.close()
    
    print("\n" + "=" * 60)
    print("[OK] DATABASE MIGRATION COMPLETE!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Migration error: {e}")
    import traceback
    traceback.print_exc()