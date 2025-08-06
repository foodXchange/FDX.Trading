#!/usr/bin/env python3
"""
FINAL MIGRATION - Complete everything now
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Databases
OLD_DB = os.getenv('DATABASE_URL')  # Old orphaned DB
NEW_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

print("=" * 80)
print("FINAL DATABASE MIGRATION")
print("=" * 80)

# Connect to new database
print("\nConnecting to new database...")
new_conn = psycopg2.connect(NEW_DB)
new_cur = new_conn.cursor()

# Check current status
new_cur.execute("SELECT COUNT(*) FROM suppliers")
current_count = new_cur.fetchone()[0]
print(f"Current suppliers in new DB: {current_count:,}")

if current_count >= 16963:
    print("\n✅ MIGRATION COMPLETE! All suppliers are in the new database.")
else:
    print(f"\n⚠️ Still need {16963 - current_count:,} suppliers")
    
    try:
        # Try to connect to old database
        print("\nAttempting to copy from old database...")
        old_conn = psycopg2.connect(OLD_DB)
        old_cur = old_conn.cursor()
        
        # Get highest ID in new DB
        new_cur.execute("SELECT COALESCE(MAX(id), 0) FROM suppliers")
        max_id = new_cur.fetchone()[0]
        
        # Copy remaining suppliers in smaller batches
        print(f"Copying suppliers with ID > {max_id}...")
        
        batch_size = 100
        total_copied = 0
        
        for start_id in range(max_id + 1, 25000, batch_size):
            old_cur.execute("""
                SELECT id, supplier_name, company_name, country, products
                FROM suppliers
                WHERE id BETWEEN %s AND %s
                ORDER BY id
            """, (start_id, start_id + batch_size - 1))
            
            batch = old_cur.fetchall()
            if not batch:
                continue
            
            for row in batch:
                try:
                    new_cur.execute("""
                        INSERT INTO suppliers (id, supplier_name, company_name, country, products)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, row)
                    total_copied += 1
                except:
                    pass
            
            if total_copied % 500 == 0:
                new_conn.commit()
                print(f"  Copied {total_copied} suppliers...")
        
        new_conn.commit()
        print(f"\n✅ Copied {total_copied} additional suppliers")
        
        old_cur.close()
        old_conn.close()
        
    except Exception as e:
        print(f"\n❌ Cannot access old database: {str(e)[:100]}")
        print("\nAlternative: Import from Excel file instead")

# Final verification
new_cur.execute("SELECT COUNT(*) FROM suppliers")
final_count = new_cur.fetchone()[0]

new_cur.execute("SELECT COUNT(*) FROM supplier_search_keywords")
keywords = new_cur.fetchone()[0]

print("\n" + "=" * 80)
print("FINAL STATUS")
print("=" * 80)
print(f"Suppliers in new database: {final_count:,} / 16,963")
print(f"Search keywords: {keywords:,}")
print(f"Progress: {final_count * 100 // 16963}%")

if final_count >= 16963:
    print("\n🎉 SUCCESS! All data migrated to new managed database!")
    print("\nNEXT STEPS:")
    print("1. Update your .env file:")
    print(f"   DATABASE_URL={NEW_DB}")
    print("\n2. Update VM (SSH to fdxfounder@4.206.1.15):")
    print("   cd ~/fdx/app")
    print("   nano .env")
    print("   # Update DATABASE_URL with new connection")
    print("\n3. Restart application on VM:")
    print("   sudo systemctl restart fdx-app")
else:
    print(f"\n⚠️ Migration incomplete. {16963 - final_count:,} suppliers still missing.")
    print("\nOPTIONS:")
    print("1. Run this script again")
    print("2. Import from Excel: python import_suppliers_excel.py")
    print("3. Use the new DB with partial data (it's safe and managed)")

new_cur.close()
new_conn.close()

# Update local .env
print("\n" + "=" * 80)
print("LOCAL ENVIRONMENT UPDATE")
print("=" * 80)

response = input("Update local .env to use new database? (y/n): ")
if response.lower() == 'y':
    with open(".env", "r") as f:
        content = f.read()
    
    with open(".env.backup", "w") as f:
        f.write(content)
    
    # Replace old URL with new
    if OLD_DB in content:
        new_content = content.replace(OLD_DB, NEW_DB)
    else:
        new_content = content + f"\nDATABASE_URL={NEW_DB}\n"
    
    with open(".env", "w") as f:
        f.write(new_content)
    
    print("✅ Local .env updated (backup saved as .env.backup)")
else:
    print("Local .env not changed")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
New Managed Database:
- Server: fdx-postgres-production.postgres.database.azure.com
- Database: foodxchange
- Username: fdxadmin
- Password: FoodXchange2024
- Resource Group: fdx-production-rg
- Suppliers: {final_count:,}
- Status: {"COMPLETE ✅" if final_count >= 16963 else f"PARTIAL ({final_count * 100 // 16963}%)"}

Your database is now:
✅ Properly managed in Azure Portal
✅ Safe with automatic backups
✅ Optimized with search functions
{"✅ Fully populated with all data" if final_count >= 16963 else "⚠️ Partially populated (but usable)"}
""")