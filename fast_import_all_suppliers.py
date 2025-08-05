import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv
import sys
from datetime import datetime

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

print("🚀 Fast Import All 23,206 Suppliers\n")

try:
    # Read Excel file
    print("📖 Reading Excel file...")
    df = pd.read_excel(r'C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx')
    print(f"✅ Found {len(df):,} suppliers in Excel file")
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Check current count
    cur.execute("SELECT COUNT(*) FROM suppliers")
    current_count = cur.fetchone()[0]
    print(f"📊 Current suppliers in database: {current_count:,}")
    
    if current_count >= 23206:
        print("✅ All suppliers already imported!")
        sys.exit(0)
    
    # Prepare data for import
    print("\n🔄 Preparing data for import...")
    suppliers_data = []
    
    for idx, row in df.iterrows():
        # Use existing product description from Excel
        products = str(row.get('Supplier\'s Description & Products', ''))
        if not products or products == 'nan':
            products = str(row.get('Products', ''))
        
        supplier = (
            str(row.get('Supplier Name', '')),
            str(row.get('Company Name', row.get('Supplier Name', ''))),
            str(row.get('Supplier\'s Country', '')),
            str(row.get('Company Email', '')),
            str(row.get('Phone', '')),
            str(row.get('Company website', '')),
            products,  # Use existing description
            str(row.get('Product Category & family (Txt)', '')),
            str(row.get('Supplier Type', '')),
            bool(row.get('Yes / No', False)),  # verified
            datetime.now(),
            datetime.now()
        )
        suppliers_data.append(supplier)
    
    # Clear existing data (optional - comment out to append)
    print("\n🗑️ Clearing existing suppliers...")
    cur.execute("TRUNCATE TABLE suppliers RESTART IDENTITY CASCADE")
    
    # Batch insert
    print(f"\n📥 Importing {len(suppliers_data):,} suppliers...")
    query = """
        INSERT INTO suppliers (
            supplier_name, company_name, country,
            company_email, company_phone, company_website,
            products, product_categories, supplier_type,
            verified, created_at, updated_at
        ) VALUES %s
    """
    
    # Import in batches
    batch_size = 1000
    total_imported = 0
    
    for i in range(0, len(suppliers_data), batch_size):
        batch = suppliers_data[i:i+batch_size]
        execute_batch(cur, query.replace('%s', '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'), batch)
        total_imported += len(batch)
        print(f"  Imported {total_imported:,} / {len(suppliers_data):,} ({total_imported*100//len(suppliers_data)}%)")
    
    # Commit
    conn.commit()
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM suppliers")
    final_count = cur.fetchone()[0]
    print(f"\n✅ SUCCESS! Total suppliers in database: {final_count:,}")
    
    # Show sample
    cur.execute("SELECT supplier_name, country, products FROM suppliers LIMIT 5")
    print("\n📋 Sample imported suppliers:")
    for row in cur.fetchall():
        print(f"  - {row[0]} ({row[1]}) - {row[2][:50]}...")
    
    cur.close()
    conn.close()
    
    print("\n🎉 Import completed successfully!")
    print("⏱️ This was FAST because we used existing product descriptions from Excel")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()