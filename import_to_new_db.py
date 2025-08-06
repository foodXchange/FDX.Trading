#!/usr/bin/env python3
"""
Import suppliers directly from Excel to new database
Faster than copying from old DB
"""

import pandas as pd
import psycopg2
from datetime import datetime

# New database connection
NEW_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

print("=" * 80)
print("IMPORTING SUPPLIERS FROM EXCEL TO NEW DATABASE")
print("=" * 80)

# Read Excel file
excel_file = r"C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx"
print(f"\nReading Excel file: {excel_file}")
df = pd.read_excel(excel_file)
print(f"Found {len(df):,} suppliers in Excel")

# Connect to new database
conn = psycopg2.connect(NEW_DB)
cur = conn.cursor()

# Check current count
cur.execute("SELECT COUNT(*) FROM suppliers")
current = cur.fetchone()[0]
print(f"Current suppliers in database: {current:,}")

if current >= len(df):
    print("All suppliers already imported!")
    exit(0)

# Clear and reimport for consistency
print("\nClearing database for fresh import...")
cur.execute("TRUNCATE TABLE supplier_search_keywords CASCADE")
cur.execute("TRUNCATE TABLE suppliers CASCADE")
conn.commit()

# Import suppliers
print("Importing suppliers...")
imported = 0
errors = 0

for idx, row in df.iterrows():
    try:
        # Extract data from Excel columns
        supplier_data = (
            idx + 1,  # id
            str(row.get('Supplier Name', '')),
            str(row.get('Company Name', '')),
            str(row.get('Country', '')),
            str(row.get('City', '')),
            str(row.get('Product / Service', '')),  # products
            str(row.get('Category', '')),  # product_categories
            str(row.get('Type', '')),  # supplier_type
            str(row.get('Company Email', '')),
            str(row.get('Company Telephone', '')),
            str(row.get('Company Website', '')),
            str(row.get('Certifications', '')),
            str(row.get('MOQ', '')),
            str(row.get('Payment Terms', '')),
            str(row.get('Lead Time', '')),
            False,  # verified
            None,  # rating
            str(row.get('Notes', '')),
            datetime.now(),  # created_at
            datetime.now(),  # updated_at
            0,  # score
            None  # product_classification
        )
        
        cur.execute("""
            INSERT INTO suppliers (
                id, supplier_name, company_name, country, city, products,
                product_categories, supplier_type, company_email, company_phone,
                company_website, certifications, minimum_order_quantity,
                payment_terms, delivery_time, verified, rating, notes,
                created_at, updated_at, score, product_classification
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, supplier_data)
        
        imported += 1
        
        if imported % 500 == 0:
            conn.commit()
            print(f"  Imported {imported}/{len(df)} suppliers...")
            
    except Exception as e:
        errors += 1
        conn.rollback()

conn.commit()
print(f"\nImported {imported} suppliers ({errors} errors)")

# Build search cache
print("\nBuilding search cache...")
keywords_list = ['oil', 'sunflower', 'chocolate', 'wafer', 'cheese', 'puff', 
                'snack', 'corn', 'organic', 'kosher', 'halal']

for keyword in keywords_list:
    cur.execute("""
        INSERT INTO supplier_search_keywords (supplier_id, keyword, keyword_type, weight)
        SELECT id, %s, 'product', 10
        FROM suppliers
        WHERE LOWER(products) LIKE '%%' || %s || '%%'
        ON CONFLICT DO NOTHING
    """, (keyword, keyword))

conn.commit()

# Final count
cur.execute("SELECT COUNT(*) FROM suppliers")
final = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM supplier_search_keywords")  
keywords = cur.fetchone()[0]

print("\n" + "=" * 80)
print("IMPORT COMPLETE!")
print("=" * 80)
print(f"Suppliers: {final:,}")
print(f"Search keywords: {keywords:,}")
print(f"\nNew database is ready with ALL data!")

cur.close()
conn.close()