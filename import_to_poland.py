import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from datetime import datetime

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

print("=" * 60)
print("IMPORTING DATA TO POLAND DATABASE")
print("=" * 60)

# Connect to Poland database
try:
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor()
    print("\n[OK] Connected to Poland database")
    
    # Create suppliers table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id SERIAL PRIMARY KEY,
            supplier_name TEXT,
            company_name TEXT,
            country TEXT,
            city TEXT,
            products TEXT,
            product_categories TEXT,
            supplier_type TEXT,
            company_email TEXT,
            company_website TEXT,
            certifications TEXT,
            rating DECIMAL,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create buyers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            id SERIAL PRIMARY KEY,
            buyer_name TEXT,
            company_name TEXT,
            country TEXT,
            city TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            product_interests TEXT,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("[OK] Tables created/verified")
    
    # Import Suppliers from Excel
    print("\n1. Importing Suppliers...")
    suppliers_file = r"C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx"
    
    if os.path.exists(suppliers_file):
        df_suppliers = pd.read_excel(suppliers_file)
        print(f"   Found {len(df_suppliers)} suppliers in Excel file")
        
        # Prepare data for insertion
        suppliers_data = []
        for _, row in df_suppliers.iterrows():
            suppliers_data.append((
                row.get('Supplier Name', ''),
                row.get('Company Name', row.get('Supplier Name', '')),
                row.get('Country', ''),
                row.get('City', ''),
                row.get('Products', ''),
                row.get('Product Categories', ''),
                row.get('Supplier Type', ''),
                row.get('Email', ''),
                row.get('Website', ''),
                row.get('Certifications', ''),
                None,  # rating
                False,  # verified
                datetime.now(),
                datetime.now()
            ))
        
        # Batch insert
        if suppliers_data:
            execute_batch(cur, """
                INSERT INTO suppliers 
                (supplier_name, company_name, country, city, products, 
                 product_categories, supplier_type, company_email, company_website,
                 certifications, rating, verified, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, suppliers_data, page_size=1000)
            
            conn.commit()
            print(f"   [OK] Imported {len(suppliers_data)} suppliers")
    else:
        print(f"   [ERROR] File not found: {suppliers_file}")
    
    # Import Buyers from CSV
    print("\n2. Importing Buyers...")
    buyers_file = r"C:\Users\foodz\Downloads\Buyers 29_7_2025.csv"
    
    if os.path.exists(buyers_file):
        df_buyers = pd.read_csv(buyers_file, encoding='utf-8-sig')
        print(f"   Found {len(df_buyers)} buyers in CSV file")
        
        # Prepare data for insertion
        buyers_data = []
        for _, row in df_buyers.iterrows():
            buyers_data.append((
                row.get('Buyer Name', row.get('Name', '')),
                row.get('Company Name', row.get('Company', '')),
                row.get('Country', ''),
                row.get('City', ''),
                row.get('Email', row.get('Contact Email', '')),
                row.get('Phone', row.get('Contact Phone', '')),
                row.get('Product Interests', row.get('Products', '')),
                False,  # verified
                datetime.now()
            ))
        
        # Batch insert
        if buyers_data:
            execute_batch(cur, """
                INSERT INTO buyers 
                (buyer_name, company_name, country, city, contact_email, 
                 contact_phone, product_interests, verified, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, buyers_data, page_size=1000)
            
            conn.commit()
            print(f"   [OK] Imported {len(buyers_data)} buyers")
    else:
        print(f"   [ERROR] File not found: {buyers_file}")
    
    # Verify import
    print("\n3. Verifying Import...")
    cur.execute("SELECT COUNT(*) FROM suppliers")
    supplier_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM buyers")
    buyer_count = cur.fetchone()[0]
    
    print(f"   [OK] Total suppliers in database: {supplier_count:,}")
    print(f"   [OK] Total buyers in database: {buyer_count:,}")
    
    # Sample data
    print("\n4. Sample Data:")
    cur.execute("SELECT supplier_name, country, city FROM suppliers LIMIT 3")
    for row in cur.fetchall():
        print(f"   - {row[0]} ({row[2]}, {row[1]})")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("[OK] IMPORT COMPLETE!")
    print("=" * 60)
    print(f"\nYour Poland database now has:")
    print(f"  - {supplier_count:,} suppliers")
    print(f"  - {buyer_count:,} buyers")
    print(f"\nAccess at: http://74.248.141.31 or http://fdx.trading")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()