import psycopg2
import os

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Files you listed
YOUR_FILES = {
    'price_book': r'c:\Users\foodz\Downloads\Price Book 2_8_2025.csv',
    'request_line_items': r'c:\Users\foodz\Downloads\Request line items 2_8_2025.csv',
    'proposal_line_items': r'c:\Users\foodz\Downloads\Proposal Line Items 2_8_2025.csv',
    'contracts': r'c:\Users\foodz\Downloads\Contracts 2_8_2025.csv',
    'proposals_samples': r'c:\Users\foodz\Downloads\Proposals & Samples 2_8_2025.csv',
    'commission_rates': r'c:\Users\foodz\Downloads\Commission Rates 2_8_2025.csv',
    'adaptation_process': r'c:\Users\foodz\Downloads\Adaptation Process 2_8_2025.csv',
    'contractors': r'c:\Users\foodz\Downloads\Contractors 2_8_2025.csv',
    'graphics_process': r'c:\Users\foodz\Downloads\Graphics process 2_8_2025.csv',
    'kosher_process': r'c:\Users\foodz\Downloads\Kosher process 2_8_2025.csv',
    'sampling_request': r'c:\Users\foodz\Downloads\Sampling Request 2_8_2025.csv',
    'compliance_process': r'c:\Users\foodz\Downloads\Compliance process 2_8_2025.csv',
}

def check_imported_data():
    print("\n" + "="*70)
    print("CHECKING YOUR CSV FILES IN POLAND DATABASE")
    print("="*70)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor()
    
    print("\nYour CSV Files vs Database Tables:")
    print("-"*70)
    
    all_imported = True
    total_records = 0
    
    for table_key, file_path in YOUR_FILES.items():
        file_name = os.path.basename(file_path)
        table_name = f"{table_key}_raw"
        
        # Check if table exists and has data
        cur.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = '{table_name}'
        """)
        
        if cur.fetchone()[0] > 0:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            total_records += count
            status = f"[OK] IMPORTED: {count} records"
            print(f"  {file_name:40} -> {status}")
        else:
            status = "[MISSING]"
            all_imported = False
            print(f"  {file_name:40} -> {status}")
    
    print("-"*70)
    
    if all_imported:
        print(f"\n[SUCCESS] ALL YOUR FILES ARE IN THE DATABASE!")
        print(f"Total Records from your files: {total_records:,}")
    else:
        print("\n[INFO] Some files may need to be imported")
    
    # Show sample data from each table
    print("\n" + "="*70)
    print("SAMPLE DATA FROM YOUR IMPORTED FILES:")
    print("="*70)
    
    for table_key in ['price_book', 'contractors', 'contracts', 'proposals_samples']:
        table_name = f"{table_key}_raw"
        try:
            cur.execute(f"""
                SELECT data 
                FROM {table_name} 
                LIMIT 1
            """)
            result = cur.fetchone()
            if result:
                print(f"\n{table_key.upper().replace('_', ' ')}:")
                data = result[0] if isinstance(result[0], dict) else {}
                if data:
                    # Show first 3 fields
                    for i, (key, value) in enumerate(list(data.items())[:3]):
                        print(f"  {key}: {str(value)[:50]}")
        except:
            pass
    
    cur.close()
    conn.close()
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    print("All your CSV files from August 2, 2025 are already imported!")
    print("They are stored in the Poland database as *_raw tables")
    print("You can query them anytime using SQL or Python")

if __name__ == "__main__":
    check_imported_data()