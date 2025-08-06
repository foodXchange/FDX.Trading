import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from datetime import datetime
import numpy as np

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# List of all CSV files to import
CSV_FILES = {
    'contractors': r'c:\Users\foodz\Downloads\Contractors 6_8_2025.csv',
    'requests': r'c:\Users\foodz\Downloads\Requests 6_8_2025.csv',
    'request_line_items': r'c:\Users\foodz\Downloads\Request line items 6_8_2025.csv',
    'products': r'c:\Users\foodz\Downloads\Products 6_8_2025.csv',
    'price_book': r'c:\Users\foodz\Downloads\Price Book 6_8_2025.csv',
    'products_category': r'c:\Users\foodz\Downloads\Products Category 6_8_2025.csv',
    'contracts': r'c:\Users\foodz\Downloads\Contracts 6_8_2025.csv',
    'proposals_samples': r'c:\Users\foodz\Downloads\Proposals & Samples 6_8_2025.csv',
    'proposal_line_items': r'c:\Users\foodz\Downloads\Proposal Line Items 6_8_2025.csv',
    'sampling_request': r'c:\Users\foodz\Downloads\Sampling Request 6_8_2025.csv',
    'adaptation_process': r'c:\Users\foodz\Downloads\Adaptation Process 6_8_2025.csv',
    'compliance_process': r'c:\Users\foodz\Downloads\Compliance process 6_8_2025.csv',
    'kosher_process': r'c:\Users\foodz\Downloads\Kosher process 6_8_2025.csv',
    'graphics_process': r'c:\Users\foodz\Downloads\Graphics process 6_8_2025.csv',
    'adaptation_steps': r'c:\Users\foodz\Downloads\Adaptation Steps 6_8_2025.csv',
    'orders': r'c:\Users\foodz\Downloads\Orders 6_8_2025.csv',
    'order_line_items': r'c:\Users\foodz\Downloads\Order Line Items 6_8_2025.csv',
    'shipping': r'c:\Users\foodz\Downloads\Shipping 6_8_2025.csv',
    'invoices': r'c:\Users\foodz\Downloads\Invoices 6_8_2025.csv',
    'commission_rates': r'c:\Users\foodz\Downloads\Commission Rates 6_8_2025.csv',
}

def clean_value(val):
    """Clean and prepare values for database insertion"""
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (int, float)):
        if np.isnan(val):
            return None
        return val
    return str(val).strip()

def create_tables(cur):
    """Create all necessary tables"""
    print("\nCreating database tables...")
    
    # Contractors table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contractors (
            id SERIAL PRIMARY KEY,
            contractor_id TEXT,
            name TEXT,
            email TEXT,
            phone TEXT,
            role TEXT,
            company TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Products tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            product_id TEXT,
            product_name TEXT,
            product_code TEXT,
            category TEXT,
            description TEXT,
            supplier_id TEXT,
            unit_price DECIMAL(10,2),
            unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products_category (
            id SERIAL PRIMARY KEY,
            category_id TEXT,
            category_name TEXT,
            parent_category TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_book (
            id SERIAL PRIMARY KEY,
            price_id TEXT,
            product_id TEXT,
            product_name TEXT,
            supplier_id TEXT,
            price DECIMAL(10,2),
            currency TEXT,
            unit TEXT,
            valid_from DATE,
            valid_to DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Request/RFQ tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id SERIAL PRIMARY KEY,
            request_id TEXT,
            request_number TEXT,
            buyer_id TEXT,
            buyer_name TEXT,
            status TEXT,
            request_date DATE,
            due_date DATE,
            total_items INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS request_line_items (
            id SERIAL PRIMARY KEY,
            line_item_id TEXT,
            request_id TEXT,
            product_id TEXT,
            product_name TEXT,
            quantity DECIMAL(10,2),
            unit TEXT,
            target_price DECIMAL(10,2),
            specifications TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Proposals tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proposals_samples (
            id SERIAL PRIMARY KEY,
            proposal_id TEXT,
            proposal_number TEXT,
            request_id TEXT,
            supplier_id TEXT,
            supplier_name TEXT,
            status TEXT,
            proposal_date DATE,
            valid_until DATE,
            total_amount DECIMAL(10,2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proposal_line_items (
            id SERIAL PRIMARY KEY,
            line_item_id TEXT,
            proposal_id TEXT,
            product_id TEXT,
            product_name TEXT,
            quantity DECIMAL(10,2),
            unit TEXT,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Orders tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_id TEXT,
            order_number TEXT,
            buyer_id TEXT,
            supplier_id TEXT,
            status TEXT,
            order_date DATE,
            delivery_date DATE,
            total_amount DECIMAL(10,2),
            payment_terms TEXT,
            shipping_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_line_items (
            id SERIAL PRIMARY KEY,
            line_item_id TEXT,
            order_id TEXT,
            product_id TEXT,
            product_name TEXT,
            quantity DECIMAL(10,2),
            unit TEXT,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Business process tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id SERIAL PRIMARY KEY,
            contract_id TEXT,
            contract_number TEXT,
            buyer_id TEXT,
            supplier_id TEXT,
            status TEXT,
            start_date DATE,
            end_date DATE,
            contract_value DECIMAL(10,2),
            terms TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shipping (
            id SERIAL PRIMARY KEY,
            shipping_id TEXT,
            order_id TEXT,
            tracking_number TEXT,
            carrier TEXT,
            status TEXT,
            ship_date DATE,
            delivery_date DATE,
            origin TEXT,
            destination TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            invoice_id TEXT,
            invoice_number TEXT,
            order_id TEXT,
            buyer_id TEXT,
            supplier_id TEXT,
            invoice_date DATE,
            due_date DATE,
            total_amount DECIMAL(10,2),
            paid_amount DECIMAL(10,2),
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS commission_rates (
            id SERIAL PRIMARY KEY,
            rate_id TEXT,
            supplier_id TEXT,
            buyer_id TEXT,
            product_category TEXT,
            commission_percentage DECIMAL(5,2),
            valid_from DATE,
            valid_to DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Process workflow tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS adaptation_process (
            id SERIAL PRIMARY KEY,
            process_id TEXT,
            order_id TEXT,
            product_id TEXT,
            step_name TEXT,
            status TEXT,
            assigned_to TEXT,
            due_date DATE,
            completed_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS compliance_process (
            id SERIAL PRIMARY KEY,
            process_id TEXT,
            product_id TEXT,
            compliance_type TEXT,
            status TEXT,
            certification_required TEXT,
            certification_obtained TEXT,
            expiry_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sampling_request (
            id SERIAL PRIMARY KEY,
            sample_id TEXT,
            request_id TEXT,
            product_id TEXT,
            supplier_id TEXT,
            quantity INTEGER,
            status TEXT,
            request_date DATE,
            received_date DATE,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("   [OK] All tables created")

def import_csv_generic(cur, table_name, file_path, column_mapping=None):
    """Generic CSV import function"""
    if not os.path.exists(file_path):
        print(f"   [SKIP] File not found: {file_path}")
        return 0
    
    try:
        # Read CSV
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        if df.empty:
            print(f"   [SKIP] No data in {file_path}")
            return 0
        
        print(f"   Importing {len(df)} records from {os.path.basename(file_path)}")
        
        # Get first row to understand structure
        if len(df) > 0:
            sample_cols = df.columns.tolist()[:10]
            print(f"      Columns: {sample_cols}...")
        
        # For now, store as JSONB for flexibility
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}_raw (
                id SERIAL PRIMARY KEY,
                data JSONB,
                source_file TEXT,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Convert DataFrame to JSON and insert
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            # Clean NaN values
            cleaned_dict = {k: (v if pd.notna(v) else None) for k, v in row_dict.items()}
            
            cur.execute(f"""
                INSERT INTO {table_name}_raw (data, source_file)
                VALUES (%s, %s)
            """, (pd.Series([cleaned_dict]).to_json(orient='records')[1:-1], file_path))
        
        return len(df)
        
    except Exception as e:
        print(f"   [ERROR] Failed to import {file_path}: {e}")
        return 0

print("=" * 60)
print("IMPORTING ALL BUSINESS DATA TO POLAND DATABASE")
print("=" * 60)

try:
    # Connect to database
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor()
    print("\n[OK] Connected to Poland database")
    
    # Create all tables
    create_tables(cur)
    conn.commit()
    
    # Import all CSV files
    print("\nImporting business data files...")
    total_records = 0
    successful_imports = 0
    
    for table_name, file_path in CSV_FILES.items():
        print(f"\n{successful_imports + 1}. Processing {table_name}...")
        records = import_csv_generic(cur, table_name, file_path)
        if records > 0:
            total_records += records
            successful_imports += 1
            conn.commit()
            print(f"   [OK] Imported {records} records")
    
    # Summary
    print("\n" + "=" * 60)
    print("IMPORT COMPLETE!")
    print("=" * 60)
    print(f"\nImport Summary:")
    print(f"  Files processed: {len(CSV_FILES)}")
    print(f"  Successful imports: {successful_imports}")
    print(f"  Total records imported: {total_records:,}")
    
    # List all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    
    print(f"\nDatabase now contains {len(tables)} tables:")
    for table in tables[:20]:  # Show first 20 tables
        cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"  - {table[0]}: {count:,} records")
    
    cur.close()
    conn.close()
    
    print("\n[OK] All business data imported to Poland database!")
    print("Database: fdx-poland-db.postgres.database.azure.com")
    
except Exception as e:
    print(f"\n[ERROR]: {e}")
    import traceback
    traceback.print_exc()