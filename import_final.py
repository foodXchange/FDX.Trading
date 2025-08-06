import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from datetime import datetime
import re

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

print("=" * 60)
print("IMPORTING DATA TO POLAND DATABASE")
print("=" * 60)

try:
    # Connect to database
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor()
    print("\n[OK] Connected to Poland database")
    
    # Import Suppliers
    print("\n1. Importing Suppliers...")
    suppliers_file = r"C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx"
    
    df = pd.read_excel(suppliers_file)
    print(f"   Found {len(df)} suppliers in Excel")
    
    # Map Excel columns to database columns
    suppliers_data = []
    for _, row in df.iterrows():
        # Extract country from address if available
        address = str(row.get('Address', ''))
        country = address.split(',')[-1].strip() if address else ''
        
        suppliers_data.append((
            row.get('Supplier Name', ''),
            row.get('Supplier Name', ''),  # company_name (use supplier name)
            row.get('Company Email', ''),
            row.get('Company website', ''),
            country,
            row.get("Supplier's Description & Products", ''),
            row.get('Product Category & family (Txt)', ''),
            'Supplier',  # supplier_type
            '',  # certifications
            None,  # rating
            False,  # verified
            datetime.now(),
            datetime.now()
        ))
    
    # Clear existing and insert new
    cur.execute("DELETE FROM suppliers")
    
    execute_batch(cur, """
        INSERT INTO suppliers 
        (supplier_name, company_name, company_email, company_website, country,
         products, product_categories, supplier_type, certifications,
         rating, verified, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, suppliers_data, page_size=1000)
    
    conn.commit()
    print(f"   [OK] Imported {len(suppliers_data)} suppliers")
    
    # Import Buyers
    print("\n2. Importing Buyers...")
    buyers_file = r"C:\Users\foodz\Downloads\Buyers 29_7_2025.csv"
    
    # Create buyers table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            id SERIAL PRIMARY KEY,
            buyer_name TEXT,
            company_name TEXT,
            contact_email TEXT,
            country TEXT,
            product_interests TEXT,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    if os.path.exists(buyers_file):
        df_buyers = pd.read_csv(buyers_file, encoding='utf-8-sig')
        print(f"   Found {len(df_buyers)} buyers in CSV")
        
        # Check available columns
        print(f"   CSV columns: {df_buyers.columns.tolist()}")
        
        buyers_data = []
        for _, row in df_buyers.iterrows():
            # Try different column name variations
            buyer_name = row.get('Buyer Name', row.get('Name', row.get('Company', '')))
            company = row.get('Company', row.get('Company Name', buyer_name))
            email = row.get('Email', row.get('Contact Email', ''))
            country = row.get('Country', '')
            products = row.get('Products', row.get('Product Interests', ''))
            
            buyers_data.append((
                buyer_name,
                company,
                email,
                country,
                products,
                False,
                datetime.now()
            ))
        
        # Clear and insert
        cur.execute("DELETE FROM buyers")
        
        execute_batch(cur, """
            INSERT INTO buyers 
            (buyer_name, company_name, contact_email, country,
             product_interests, verified, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, buyers_data, page_size=1000)
        
        conn.commit()
        print(f"   [OK] Imported {len(buyers_data)} buyers")
    
    # Verify import
    print("\n3. Verification:")
    cur.execute("SELECT COUNT(*) FROM suppliers")
    supplier_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM buyers")
    buyer_count = cur.fetchone()[0]
    
    print(f"   Suppliers in database: {supplier_count:,}")
    print(f"   Buyers in database: {buyer_count:,}")
    
    # Sample data
    print("\n4. Sample Suppliers:")
    cur.execute("SELECT supplier_name, country, company_email FROM suppliers WHERE company_email != '' LIMIT 5")
    for row in cur.fetchall():
        print(f"   - {row[0][:50]} ({row[1]}) - {row[2]}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("IMPORT COMPLETE!")
    print("=" * 60)
    print(f"\nPoland database now contains:")
    print(f"  - {supplier_count:,} suppliers")
    print(f"  - {buyer_count:,} buyers")
    print(f"\nDatabase: fdx-poland-db.postgres.database.azure.com")
    print(f"Access your app at: http://74.248.141.31 or http://fdx.trading")
    
except Exception as e:
    print(f"\n[ERROR]: {e}")
    import traceback
    traceback.print_exc()