import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Get connection string from environment
conn_str = os.getenv('DATABASE_URL')
if not conn_str:
    # Use hardcoded if env not available
    conn_str = "postgresql://fdxadmin:FDX2030!@foodxchange-flex-db.postgres.database.azure.com:5432/foodxchange?sslmode=require"

conn = psycopg2.connect(conn_str)
cur = conn.cursor()

cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN products IS NOT NULL AND LENGTH(products) > 10 THEN 1 END) as enhanced
    FROM suppliers
""")
stats = cur.fetchone()

print(f"Enhancement Progress:")
print(f"Total suppliers: {stats[0]:,}")
print(f"Enhanced: {stats[1]:,} ({stats[1]*100//stats[0]}%)")
print(f"Remaining: {stats[0] - stats[1]:,}")

# Show some recently enhanced
cur.execute("""
    SELECT supplier_name, products 
    FROM suppliers 
    WHERE products IS NOT NULL 
    AND LENGTH(products) > 50
    ORDER BY id DESC
    LIMIT 5
""")

print("\nRecently enhanced suppliers:")
for row in cur.fetchall():
    print(f"- {row[0][:50]}...")
    print(f"  Products: {row[1][:80]}...")

cur.close()
conn.close()