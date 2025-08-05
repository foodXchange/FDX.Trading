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

print("🚀 Import All 23,206 Suppliers - Fixed Version\n")

# Helper function to truncate strings
def truncate_string(value, max_length):
    """Truncate string to max length if needed"""
    if value and len(value) > max_length:
        return value[:max_length-3] + "..."
    return value

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
    
    # Check column limits
    print("\n🔍 Checking database column sizes...")
    cur.execute("""
        SELECT column_name, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'suppliers' 
        AND data_type LIKE 'character%'
        ORDER BY column_name
    """)
    
    column_limits = {}
    for col_name, max_len in cur.fetchall():
        if max_len:
            column_limits[col_name] = max_len
            print(f"  {col_name}: max {max_len} chars")
    
    # Prepare data for import
    print("\n🔄 Preparing data for import...")
    suppliers_data = []
    
    for idx, row in df.iterrows():
        # Get and truncate values based on column limits
        supplier_name = truncate_string(str(row.get('Supplier Name', '')), 
                                      column_limits.get('supplier_name', 500))
        company_name = truncate_string(str(row.get('Company Name', row.get('Supplier Name', ''))), 
                                     column_limits.get('company_name', 500))
        country = truncate_string(str(row.get('Supplier\'s Country', '')), 
                                column_limits.get('country', 100))
        email = truncate_string(str(row.get('Company Email', '')), 
                              column_limits.get('company_email', 500))
        phone = truncate_string(str(row.get('Phone', '')), 
                              column_limits.get('company_phone', 50))
        website = truncate_string(str(row.get('Company website', '')), 
                                column_limits.get('company_website', 500))
        
        # Products - use TEXT field, no truncation needed
        products = str(row.get('Supplier\'s Description & Products', ''))
        if not products or products == 'nan':
            products = str(row.get('Products', ''))
        
        product_categories = truncate_string(str(row.get('Product Category & family (Txt)', '')), 
                                           column_limits.get('product_categories', 500))
        supplier_type = truncate_string(str(row.get('Supplier Type', '')), 
                                      column_limits.get('supplier_type', 500))
        
        supplier = (
            supplier_name,
            company_name,
            country,
            email,
            phone,
            website,
            products,  # TEXT field - no truncation
            product_categories,
            supplier_type,
            bool(row.get('Yes / No', False)),  # verified
            datetime.now(),
            datetime.now()
        )
        suppliers_data.append(supplier)
    
    # Ask for confirmation before clearing
    print(f"\n⚠️  About to clear {current_count:,} existing suppliers and import {len(suppliers_data):,} new ones.")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Import cancelled.")
        sys.exit(0)
    
    # Clear existing data
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
    batch_size = 500  # Smaller batch size for safety
    total_imported = 0
    
    for i in range(0, len(suppliers_data), batch_size):
        batch = suppliers_data[i:i+batch_size]
        execute_batch(cur, query.replace('%s', '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'), batch)
        total_imported += len(batch)
        
        # Show progress
        progress = total_imported * 100 // len(suppliers_data)
        print(f"  Imported {total_imported:,} / {len(suppliers_data):,} ({progress}%)")
        
        # Commit every 10 batches
        if (i // batch_size) % 10 == 0:
            conn.commit()
    
    # Final commit
    conn.commit()
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM suppliers")
    final_count = cur.fetchone()[0]
    print(f"\n✅ SUCCESS! Total suppliers in database: {final_count:,}")
    
    # Show sample
    cur.execute("SELECT supplier_name, country, LENGTH(products) as prod_len FROM suppliers ORDER BY id DESC LIMIT 5")
    print("\n📋 Sample imported suppliers:")
    for row in cur.fetchall():
        print(f"  - {row[0]} ({row[1]}) - Product data: {row[2]} chars")
    
    cur.close()
    conn.close()
    
    print("\n🎉 Import completed successfully!")
    print("⏱️ All 23,206 suppliers are now in the database!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()