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
    
    print("✅ Connected to PostgreSQL Database!\n")
    
    # Get total suppliers
    cur.execute("SELECT COUNT(*) FROM suppliers")
    total = cur.fetchone()[0]
    print(f"📊 Total suppliers: {total:,}")
    
    # Get country distribution
    cur.execute("""
        SELECT country, COUNT(*) as count 
        FROM suppliers 
        GROUP BY country 
        ORDER BY count DESC 
        LIMIT 5
    """)
    print("\n🌍 Top 5 countries:")
    for country, count in cur.fetchall():
        print(f"   {country}: {count:,} suppliers")
    
    # Get sample suppliers
    cur.execute("""
        SELECT supplier_name, country, products 
        FROM suppliers 
        WHERE products IS NOT NULL 
        LIMIT 3
    """)
    print("\n📦 Sample suppliers with products:")
    for name, country, products in cur.fetchall():
        print(f"\n   {name} ({country})")
        print(f"   Products: {products[:100]}..." if len(products) > 100 else f"   Products: {products}")
    
    # Check AI enhancement
    cur.execute("""
        SELECT 
            COUNT(CASE WHEN products IS NOT NULL AND LENGTH(products) > 200 THEN 1 END) as enhanced,
            COUNT(*) as total
        FROM suppliers
    """)
    enhanced, total = cur.fetchone()
    print(f"\n🤖 AI Enhancement: {enhanced:,} / {total:,} ({enhanced*100//total}%)")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")