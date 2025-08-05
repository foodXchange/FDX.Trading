import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

print("🧹 Supplier Deduplication Script\n")

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # First, backup current count
    cur.execute("SELECT COUNT(*) FROM suppliers")
    initial_count = cur.fetchone()[0]
    print(f"📊 Initial supplier count: {initial_count:,}")
    
    # Strategy: Keep the record with the most complete data (longest products description)
    # and earliest created_at timestamp
    
    print("\n🔍 Finding and removing duplicates...")
    
    # Step 1: Remove exact duplicates (same name, country, email)
    cur.execute('''
        WITH duplicates AS (
            SELECT id,
                   supplier_name,
                   country,
                   company_email,
                   LENGTH(COALESCE(products, '')) as product_length,
                   created_at,
                   ROW_NUMBER() OVER (
                       PARTITION BY supplier_name, country, COALESCE(company_email, 'no_email')
                       ORDER BY LENGTH(COALESCE(products, '')) DESC, created_at ASC
                   ) as rn
            FROM suppliers
        )
        DELETE FROM suppliers
        WHERE id IN (
            SELECT id FROM duplicates WHERE rn > 1
        )
    ''')
    
    exact_removed = cur.rowcount
    print(f"✅ Removed {exact_removed:,} exact duplicates")
    
    # Step 2: Handle case-insensitive duplicates
    cur.execute('''
        WITH case_duplicates AS (
            SELECT id,
                   supplier_name,
                   country,
                   LENGTH(COALESCE(products, '')) as product_length,
                   created_at,
                   ROW_NUMBER() OVER (
                       PARTITION BY LOWER(supplier_name), country
                       ORDER BY LENGTH(COALESCE(products, '')) DESC, created_at ASC
                   ) as rn
            FROM suppliers
        )
        DELETE FROM suppliers
        WHERE id IN (
            SELECT id FROM case_duplicates WHERE rn > 1
        )
    ''')
    
    case_removed = cur.rowcount
    print(f"✅ Removed {case_removed:,} case-insensitive duplicates")
    
    # Step 3: Remove duplicates with same email (keep best record)
    cur.execute('''
        WITH email_duplicates AS (
            SELECT id,
                   supplier_name,
                   company_email,
                   LENGTH(COALESCE(products, '')) as product_length,
                   created_at,
                   ROW_NUMBER() OVER (
                       PARTITION BY company_email
                       ORDER BY LENGTH(COALESCE(products, '')) DESC, created_at ASC
                   ) as rn
            FROM suppliers
            WHERE company_email IS NOT NULL 
            AND company_email != ''
            AND company_email != 'nan'
        )
        DELETE FROM suppliers
        WHERE id IN (
            SELECT id FROM email_duplicates WHERE rn > 1
        )
    ''')
    
    email_removed = cur.rowcount
    print(f"✅ Removed {email_removed:,} email duplicates")
    
    # Step 4: Clean up 'nan' emails
    cur.execute('''
        UPDATE suppliers 
        SET company_email = NULL 
        WHERE company_email = 'nan'
    ''')
    
    nan_cleaned = cur.rowcount
    print(f"✅ Cleaned {nan_cleaned:,} 'nan' email entries")
    
    # Get final count
    cur.execute("SELECT COUNT(*) FROM suppliers")
    final_count = cur.fetchone()[0]
    
    # Commit changes
    conn.commit()
    
    print(f"\n📈 Deduplication Summary:")
    print(f"   Initial suppliers: {initial_count:,}")
    print(f"   Exact duplicates removed: {exact_removed:,}")
    print(f"   Case duplicates removed: {case_removed:,}")
    print(f"   Email duplicates removed: {email_removed:,}")
    print(f"   Total removed: {initial_count - final_count:,}")
    print(f"   Final suppliers: {final_count:,}")
    print(f"   Reduction: {((initial_count - final_count) / initial_count * 100):.1f}%")
    
    # Show some statistics
    cur.execute("SELECT COUNT(DISTINCT supplier_name) FROM suppliers")
    unique_names = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(DISTINCT LOWER(company_email)) FROM suppliers WHERE company_email IS NOT NULL")
    unique_emails = cur.fetchone()[0]
    
    print(f"\n✨ Final Database Quality:")
    print(f"   Unique supplier names: {unique_names:,}")
    print(f"   Unique emails: {unique_emails:,}")
    print(f"   Data integrity: {'✅ Good' if unique_names == final_count else '⚠️  Still has duplicates'}")
    
    # Check if any major duplicates remain
    cur.execute('''
        SELECT supplier_name, COUNT(*) as count
        FROM suppliers 
        GROUP BY supplier_name 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 5
    ''')
    
    remaining_dups = cur.fetchall()
    if remaining_dups:
        print(f"\n⚠️  Some duplicates remain (different countries/variations):")
        for name, count in remaining_dups:
            print(f"   {name}: {count} records")
    else:
        print(f"\n✅ No duplicate names remaining!")
    
    cur.close()
    conn.close()
    
    print("\n🎉 Deduplication complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if conn:
        conn.rollback()