import psycopg2
import os
from dotenv import load_dotenv
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Connection string for recovered database
recovered_db_url = os.getenv('DATABASE_URL').replace('fdx-postgres-server', 'fdx-postgres-recovered')

print("🔍 Checking recovered database...")
print(f"Connecting to: fdx-postgres-recovered")

try:
    conn = psycopg2.connect(recovered_db_url)
    cur = conn.cursor()
    
    # Check suppliers count
    cur.execute("SELECT COUNT(*) FROM suppliers")
    count = cur.fetchone()[0]
    print(f"\n✅ Suppliers in recovered database: {count:,}")
    
    if count > 20000:
        print("\n🎉 SUCCESS! Found the complete database with all suppliers!")
        
        # Show some sample data
        cur.execute("""
            SELECT supplier_name, country, company_email 
            FROM suppliers 
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        print("\nLatest imported suppliers:")
        for row in cur.fetchall():
            print(f"  - {row[0]} ({row[1]}) - {row[2]}")
    else:
        print(f"\n⚠️ Recovered database has {count} suppliers, not the expected 23,206")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("The recovered server might still be provisioning. Please wait and try again.")