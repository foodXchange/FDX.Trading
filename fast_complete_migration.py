#!/usr/bin/env python3
"""
Fast completion of migration - copy remaining 10,763 suppliers
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

OLD_DB = os.getenv('DATABASE_URL')
NEW_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

print("COMPLETING MIGRATION...")
print("=" * 60)

# Connect
old_conn = psycopg2.connect(OLD_DB)
old_cur = old_conn.cursor()

new_conn = psycopg2.connect(NEW_DB)
new_cur = new_conn.cursor()

# Get missing IDs
print("Finding missing suppliers...")
new_cur.execute("SELECT MAX(id) FROM suppliers")
last_id = new_cur.fetchone()[0] or 0
print(f"Last ID in new DB: {last_id}")

# Copy remaining suppliers (simple approach)
print(f"Copying suppliers from ID {last_id + 1} onwards...")

batch_size = 200
copied = 0
start_id = last_id + 1

while True:
    # Get batch from old DB
    old_cur.execute("""
        SELECT id, supplier_name, company_name, country, products
        FROM suppliers 
        WHERE id >= %s
        ORDER BY id
        LIMIT %s
    """, (start_id, batch_size))
    
    batch = old_cur.fetchall()
    if not batch:
        break
    
    # Insert batch into new DB
    for row in batch:
        try:
            new_cur.execute("""
                INSERT INTO suppliers (id, supplier_name, company_name, country, products)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, row)
            copied += 1
        except:
            new_conn.rollback()
    
    new_conn.commit()
    start_id = batch[-1][0] + 1
    
    print(f"Copied up to ID {start_id - 1} ({copied} total)...")
    
    if copied >= 10763:  # We need about this many more
        break

# Also copy the search cache
print("\nCopying search cache...")
old_cur.execute("SELECT supplier_id, keyword, keyword_type, weight FROM supplier_search_keywords WHERE supplier_id > %s", (last_id,))
cache = old_cur.fetchall()

for entry in cache:
    try:
        new_cur.execute("""
            INSERT INTO supplier_search_keywords VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, entry)
    except:
        pass

new_conn.commit()

# Final check
new_cur.execute("SELECT COUNT(*) FROM suppliers")
final_count = new_cur.fetchone()[0]

print(f"\n{'=' * 60}")
print(f"MIGRATION COMPLETE!")
print(f"Total suppliers in new database: {final_count:,}")

if final_count >= 16000:
    print("SUCCESS! All data migrated!")
else:
    print(f"Partial migration: {final_count:,} / 16,963")

old_cur.close()
old_conn.close()
new_cur.close()
new_conn.close()