import psycopg2
import os
from dotenv import load_dotenv
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

try:
    # Connect to database
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("🔍 Checking supplier import times...\n")
    
    # Check earliest and latest created_at times
    cur.execute("""
        SELECT 
            MIN(created_at) as earliest,
            MAX(created_at) as latest,
            COUNT(*) as total
        FROM suppliers
    """)
    earliest, latest, total = cur.fetchone()
    
    print(f"📊 Import Summary:")
    print(f"   Total suppliers: {total:,}")
    print(f"   Earliest import: {earliest}")
    print(f"   Latest import: {latest}")
    
    # Check imports by date
    cur.execute("""
        SELECT 
            DATE(created_at) as import_date,
            COUNT(*) as count
        FROM suppliers
        GROUP BY DATE(created_at)
        ORDER BY import_date DESC
    """)
    
    print("\n📅 Imports by date:")
    for date, count in cur.fetchall():
        print(f"   {date}: {count:,} suppliers")
    
    # Check if there's updated_at info
    cur.execute("""
        SELECT COUNT(*) 
        FROM suppliers 
        WHERE updated_at != created_at
    """)
    updated_count = cur.fetchone()[0]
    print(f"\n🔄 Updated records: {updated_count}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")