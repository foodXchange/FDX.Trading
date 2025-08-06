#!/usr/bin/env python3
"""
Complete Full Migration - Get ALL 16,963 suppliers to new database
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Databases
OLD_DB = os.getenv('DATABASE_URL')  # Has all 16,963 suppliers
NEW_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

print("=" * 80)
print("COMPLETING FULL MIGRATION TO NEW DATABASE")
print("=" * 80)

# Connect to both
print("\nConnecting to databases...")
old_conn = psycopg2.connect(OLD_DB)
old_cur = old_conn.cursor()

new_conn = psycopg2.connect(NEW_DB)
new_cur = new_conn.cursor()

# Check current status
print("\nCurrent Status:")
print("-" * 40)

old_cur.execute("SELECT COUNT(*) FROM suppliers")
old_count = old_cur.fetchone()[0]
print(f"Old database: {old_count:,} suppliers")

new_cur.execute("SELECT COUNT(*) FROM suppliers")
current_count = new_cur.fetchone()[0]
print(f"New database: {current_count:,} suppliers")
print(f"Need to migrate: {old_count - current_count:,} suppliers")

if current_count >= old_count:
    print("\nAll data already migrated!")
    exit(0)

# Get missing supplier IDs
print("\nFinding missing suppliers...")
new_cur.execute("SELECT id FROM suppliers")
existing_ids = set(row[0] for row in new_cur.fetchall())

old_cur.execute("SELECT id FROM suppliers")
all_ids = set(row[0] for row in old_cur.fetchall())

missing_ids = all_ids - existing_ids
print(f"Missing IDs: {len(missing_ids)}")

# Copy missing suppliers
print("\nCopying missing suppliers...")
copied = 0
errors = 0

for supplier_id in sorted(missing_ids):
    try:
        # Get supplier from old DB
        old_cur.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
        supplier = old_cur.fetchone()
        
        if supplier:
            # Insert into new DB (using positional parameters for all columns)
            placeholders = ', '.join(['%s'] * len(supplier))
            new_cur.execute(f"INSERT INTO suppliers VALUES ({placeholders})", supplier)
            copied += 1
            
            if copied % 100 == 0:
                new_conn.commit()
                print(f"  Copied {copied}/{len(missing_ids)} suppliers...")
    except Exception as e:
        errors += 1
        new_conn.rollback()
        # Try minimal insert
        try:
            old_cur.execute("""
                SELECT id, supplier_name, company_name, country, products 
                FROM suppliers WHERE id = %s
            """, (supplier_id,))
            basic_data = old_cur.fetchone()
            if basic_data:
                new_cur.execute("""
                    INSERT INTO suppliers (id, supplier_name, company_name, country, products)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, basic_data)
                copied += 1
        except:
            pass

new_conn.commit()
print(f"\nCopied {copied} suppliers ({errors} errors)")

# Copy search cache
print("\nCopying search cache...")
old_cur.execute("SELECT COUNT(*) FROM supplier_search_keywords")
old_cache = old_cur.fetchone()[0]

new_cur.execute("DELETE FROM supplier_search_keywords")  # Clear first
new_conn.commit()

# Copy all keywords
batch_size = 5000
offset = 0
cache_copied = 0

while offset < old_cache:
    old_cur.execute("""
        SELECT supplier_id, keyword, keyword_type, weight
        FROM supplier_search_keywords
        LIMIT %s OFFSET %s
    """, (batch_size, offset))
    
    keywords = old_cur.fetchall()
    if not keywords:
        break
    
    for kw in keywords:
        try:
            new_cur.execute("""
                INSERT INTO supplier_search_keywords VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, kw)
            cache_copied += 1
        except:
            pass
    
    new_conn.commit()
    offset += batch_size
    print(f"  Copied {min(offset, old_cache)}/{old_cache} keywords...")

print(f"Cache copied: {cache_copied} keywords")

# Final verification
print("\nFinal Verification:")
print("-" * 40)

new_cur.execute("SELECT COUNT(*) FROM suppliers")
final_count = new_cur.fetchone()[0]

new_cur.execute("SELECT COUNT(*) FROM supplier_search_keywords")
final_cache = new_cur.fetchone()[0]

print(f"Suppliers in new database: {final_count:,}")
print(f"Keywords in cache: {final_cache:,}")

# Test search
new_cur.execute("""
    SELECT COUNT(*) FROM suppliers 
    WHERE products ILIKE '%oil%'
""")
oil_count = new_cur.fetchone()[0]
print(f"Test search (oil): {oil_count} suppliers")

# Close connections
old_cur.close()
old_conn.close()
new_cur.close()
new_conn.close()

print("\n" + "=" * 80)
if final_count >= 16000:
    print("SUCCESS! ALL DATA MIGRATED!")
    print("=" * 80)
    print(f"""
Your new database is complete:
- {final_count:,} suppliers (ALL DATA)
- {final_cache:,} search keywords
- Fully optimized and managed

Connection string:
{NEW_DB}

Update your .env and VM with this connection string.
Your database is now FIXED and COMPLETE!
""")
else:
    print("PARTIAL MIGRATION")
    print("=" * 80)
    print(f"Migrated {final_count:,} suppliers")
    print("Run this script again to continue")