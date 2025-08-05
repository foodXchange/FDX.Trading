import psycopg2
import os
from dotenv import load_dotenv
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print('🔍 Checking for duplicate suppliers...\n')
    
    # Check duplicates by supplier_name
    cur.execute('''
        SELECT supplier_name, COUNT(*) as count
        FROM suppliers 
        GROUP BY supplier_name 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 20
    ''')
    
    duplicates = cur.fetchall()
    if duplicates:
        print(f'⚠️  Found duplicate supplier names:')
        total_name_dups = 0
        for name, count in duplicates[:10]:
            print(f'   "{name}": {count} records')
            total_name_dups += (count - 1)
        if len(duplicates) > 10:
            print(f'   ... and {len(duplicates)-10} more duplicate names')
    else:
        print('✅ No duplicate supplier names found')
    
    # Check duplicates by company_email
    cur.execute('''
        SELECT company_email, COUNT(*) as count
        FROM suppliers 
        WHERE company_email IS NOT NULL AND company_email != ''
        GROUP BY company_email 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 20
    ''')
    
    email_dups = cur.fetchall()
    print(f'\n📧 Email duplicates:')
    if email_dups:
        print(f'Found duplicate emails:')
        for email, count in email_dups[:10]:
            print(f'   {email}: {count} records')
        if len(email_dups) > 10:
            print(f'   ... and {len(email_dups)-10} more duplicate emails')
    else:
        print('✅ No duplicate emails found')
    
    # Check similar names (potential duplicates)
    cur.execute('''
        SELECT a.id, a.supplier_name, b.id, b.supplier_name, a.country
        FROM suppliers a
        JOIN suppliers b ON a.id < b.id
        WHERE LOWER(REPLACE(a.supplier_name, ' ', '')) = LOWER(REPLACE(b.supplier_name, ' ', ''))
           OR (a.company_email = b.company_email AND a.company_email IS NOT NULL AND a.company_email != '')
        LIMIT 20
    ''')
    
    similar = cur.fetchall()
    print(f'\n🔄 Potential duplicates (similar names or same email):')
    if similar:
        print(f'Found potential duplicates:')
        for id1, name1, id2, name2, country in similar[:10]:
            print(f'   ID {id1}: "{name1}" vs ID {id2}: "{name2}" ({country})')
        if len(similar) > 10:
            print(f'   ... and {len(similar)-10} more potential duplicates')
    else:
        print('✅ No similar records found')
    
    # Get total counts
    cur.execute('SELECT COUNT(DISTINCT supplier_name) FROM suppliers')
    unique_names = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM suppliers')
    total = cur.fetchone()[0]
    
    print(f'\n📊 Summary:')
    print(f'   Total suppliers: {total:,}')
    print(f'   Unique supplier names: {unique_names:,}')
    print(f'   Potential duplicates: {total - unique_names:,}')
    
    # Show some examples of duplicates
    if duplicates:
        print(f'\n📋 Example duplicate: "{duplicates[0][0]}"')
        cur.execute('''
            SELECT id, supplier_name, country, company_email, created_at
            FROM suppliers 
            WHERE supplier_name = %s
            ORDER BY created_at
        ''', (duplicates[0][0],))
        
        examples = cur.fetchall()
        for id, name, country, email, created in examples:
            print(f'   ID {id}: {name} ({country}) - {email} - Created: {created}')
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')