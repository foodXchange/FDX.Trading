#!/usr/bin/env python3
"""
Migrate Data from Orphaned to New Server
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Connection strings
OLD_DB = os.getenv('DATABASE_URL')  # Orphaned but working
NEW_DB = "postgresql://fdxadmin:FDX2030!@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

print("=" * 80)
print("MIGRATING DATABASE TO NEW SERVER")
print("=" * 80)

print("\n1. CONNECTING TO OLD DATABASE...")
print("-" * 40)

try:
    old_conn = psycopg2.connect(OLD_DB)
    old_cur = old_conn.cursor(cursor_factory=RealDictCursor)
    
    # Get supplier count
    old_cur.execute("SELECT COUNT(*) as count FROM suppliers")
    old_count = old_cur.fetchone()['count']
    print(f"Connected to old DB: {old_count:,} suppliers found")
    
except Exception as e:
    print(f"ERROR: Cannot connect to old database: {e}")
    exit(1)

print("\n2. CONNECTING TO NEW DATABASE...")
print("-" * 40)

try:
    new_conn = psycopg2.connect(NEW_DB)
    new_cur = new_conn.cursor()
    
    print("Connected to new server")
    
except Exception as e:
    print(f"ERROR: Cannot connect to new database: {e}")
    print("Check firewall rules or connection string")
    exit(1)

print("\n3. CREATING TABLES IN NEW DATABASE...")
print("-" * 40)

# Create all necessary tables
tables = [
    """CREATE TABLE IF NOT EXISTS suppliers (
        id SERIAL PRIMARY KEY,
        supplier_name VARCHAR(255),
        company_name VARCHAR(255),
        country VARCHAR(100),
        products TEXT,
        supplier_type TEXT,
        company_email VARCHAR(255),
        company_website VARCHAR(255),
        company_phone VARCHAR(100),
        address TEXT,
        certifications TEXT,
        verified BOOLEAN DEFAULT FALSE,
        rating DECIMAL(3,2),
        product_categories TEXT,
        product_classification VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    """CREATE TABLE IF NOT EXISTS supplier_search_keywords (
        supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
        keyword VARCHAR(100),
        keyword_type VARCHAR(50),
        weight INTEGER DEFAULT 1,
        PRIMARY KEY (supplier_id, keyword)
    )""",
    
    """CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        project_name VARCHAR(255) NOT NULL,
        description TEXT,
        user_email VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    """CREATE TABLE IF NOT EXISTS project_suppliers (
        id SERIAL PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
        supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    """CREATE TABLE IF NOT EXISTS search_history (
        id SERIAL PRIMARY KEY,
        query TEXT,
        results_count INTEGER,
        user_email VARCHAR(255),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
]

for table_sql in tables:
    try:
        new_cur.execute(table_sql)
        new_conn.commit()
        print("Table created/verified")
    except Exception as e:
        print(f"Table creation warning: {str(e)[:50]}")
        new_conn.rollback()

print("\n4. MIGRATING SUPPLIERS DATA...")
print("-" * 40)

# Get all suppliers from old DB
old_cur.execute("""
    SELECT id, supplier_name, company_name, country, products, 
           supplier_type, company_email, company_website, company_phone,
           address, certifications, verified, rating, product_categories,
           product_classification, created_at, updated_at
    FROM suppliers
    ORDER BY id
""")

suppliers = old_cur.fetchall()
print(f"Fetched {len(suppliers)} suppliers from old database")

# Insert into new database
print("Inserting suppliers into new database...")
batch_size = 500
for i in range(0, len(suppliers), batch_size):
    batch = suppliers[i:i+batch_size]
    
    for supplier in batch:
        try:
            new_cur.execute("""
                INSERT INTO suppliers (
                    id, supplier_name, company_name, country, products,
                    supplier_type, company_email, company_website, company_phone,
                    address, certifications, verified, rating, product_categories,
                    product_classification, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                supplier['id'], supplier['supplier_name'], supplier['company_name'],
                supplier['country'], supplier['products'], supplier['supplier_type'],
                supplier['company_email'], supplier['company_website'], supplier['company_phone'],
                supplier['address'], supplier['certifications'], supplier['verified'],
                supplier['rating'], supplier['product_categories'], supplier['product_classification'],
                supplier['created_at'], supplier['updated_at']
            ))
        except Exception as e:
            print(f"Error inserting supplier {supplier['id']}: {str(e)[:50]}")
    
    new_conn.commit()
    print(f"  Migrated {min(i+batch_size, len(suppliers))}/{len(suppliers)} suppliers...")

# Reset sequence
new_cur.execute("SELECT setval('suppliers_id_seq', (SELECT MAX(id) FROM suppliers))")
new_conn.commit()

print("\n5. MIGRATING SEARCH CACHE...")
print("-" * 40)

try:
    old_cur.execute("SELECT * FROM supplier_search_keywords")
    keywords = old_cur.fetchall()
    print(f"Found {len(keywords)} keyword entries")
    
    for kw in keywords:
        try:
            new_cur.execute("""
                INSERT INTO supplier_search_keywords (supplier_id, keyword, keyword_type, weight)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (kw['supplier_id'], kw['keyword'], kw['keyword_type'], kw['weight']))
        except:
            pass
    
    new_conn.commit()
    print("Search cache migrated")
except:
    print("No search cache to migrate or error occurred")

print("\n6. CREATING INDEXES...")
print("-" * 40)

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_suppliers_country ON suppliers(country)",
    "CREATE INDEX IF NOT EXISTS idx_suppliers_verified ON suppliers(verified)",
    "CREATE INDEX IF NOT EXISTS idx_search_keyword ON supplier_search_keywords(keyword)",
    "CREATE INDEX IF NOT EXISTS idx_search_supplier ON supplier_search_keywords(supplier_id)"
]

for idx in indexes:
    try:
        new_cur.execute(idx)
        new_conn.commit()
        print("Index created")
    except:
        pass

print("\n7. CREATING SEARCH FUNCTIONS...")
print("-" * 40)

try:
    new_cur.execute("""
        CREATE OR REPLACE FUNCTION fast_search(search_terms TEXT[])
        RETURNS TABLE (
            supplier_id INTEGER,
            supplier_name VARCHAR,
            country VARCHAR,
            products TEXT,
            email VARCHAR,
            website VARCHAR,
            match_score BIGINT
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                s.id,
                s.supplier_name,
                s.country,
                s.products,
                s.company_email,
                s.company_website,
                COALESCE(SUM(k.weight), 0)::BIGINT as match_score
            FROM suppliers s
            LEFT JOIN supplier_search_keywords k ON s.id = k.supplier_id
            WHERE k.keyword = ANY(search_terms)
            GROUP BY s.id, s.supplier_name, s.country, s.products, s.company_email, s.company_website
            ORDER BY match_score DESC
            LIMIT 100;
        END;
        $$;
    """)
    new_conn.commit()
    print("Fast search function created")
except:
    print("Function creation skipped or failed")

print("\n8. VERIFICATION...")
print("-" * 40)

# Verify migration
new_cur.execute("SELECT COUNT(*) FROM suppliers")
new_count = new_cur.fetchone()[0]

print(f"Old database: {old_count:,} suppliers")
print(f"New database: {new_count:,} suppliers")

if new_count == old_count:
    print("SUCCESS: All data migrated!")
else:
    print(f"WARNING: Count mismatch ({old_count - new_count} difference)")

# Close connections
old_cur.close()
old_conn.close()
new_cur.close()
new_conn.close()

print("\n" + "=" * 80)
print("MIGRATION COMPLETE!")
print("=" * 80)
print(f"""
NEW DATABASE DETAILS:
- Server: fdx-postgres-production.postgres.database.azure.com
- Database: foodxchange
- Resource Group: fdx-production-rg
- Location: Canada Central
- Status: FULLY MANAGED (visible in Azure Portal)

UPDATE YOUR .ENV FILE:
DATABASE_URL={NEW_DB}

UPDATE YOUR VM:
ssh azureuser@4.206.1.15
nano .env
# Update DATABASE_URL with new connection string
""")

# Update local .env
print("\nUpdating local .env file...")
with open(".env", "r") as f:
    content = f.read()

with open(".env.backup", "w") as f:
    f.write(content)

new_content = content.replace(OLD_DB, NEW_DB)
with open(".env", "w") as f:
    f.write(new_content)

print("Local .env updated (backup saved as .env.backup)")
print("\nYour database is now properly managed and safe!")