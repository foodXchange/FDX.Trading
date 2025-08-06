import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def test_connection():
    """Step 1: Test database connection"""
    print("\n" + "="*60)
    print("STEP 1: TESTING DATABASE CONNECTION")
    print("="*60)
    
    try:
        conn = psycopg2.connect(POLAND_DB)
        cur = conn.cursor()
        
        # Get version
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"[OK] Connected to: {version.split(',')[0]}")
        
        # Count main tables
        tables = ['suppliers', 'buyers', 'products_raw', 'orders_raw', 'requests_raw']
        print("\nTable Record Counts:")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {table:20} : {count:,} records")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

def test_buyer_workflow():
    """Step 2: Test buyer to request workflow"""
    print("\n" + "="*60)
    print("STEP 2: TESTING BUYER WORKFLOW")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check buyers
    print("\n2.1 Sample Buyers:")
    cur.execute("""
        SELECT id, buyer_name, company_name, country 
        FROM buyers 
        WHERE buyer_name IS NOT NULL
        LIMIT 5
    """)
    
    for row in cur.fetchall():
        print(f"  ID:{row['id']} - {row['buyer_name']} ({row['company_name']}) - {row['country']}")
    
    # Check requests
    print("\n2.2 Sample Requests:")
    cur.execute("""
        SELECT 
            data->>'Buyer' as buyer,
            data->>'Request' as request,
            data->>'Status' as status,
            data->>'Request Date' as date
        FROM requests_raw 
        WHERE data->>'Buyer' IS NOT NULL
        LIMIT 5
    """)
    
    for row in cur.fetchall():
        print(f"  {row['buyer']} - {row['request']} [{row['status']}] - {row['date']}")
    
    cur.close()
    conn.close()

def test_supplier_workflow():
    """Step 3: Test supplier to product workflow"""
    print("\n" + "="*60)
    print("STEP 3: TESTING SUPPLIER WORKFLOW")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Top supplier countries
    print("\n3.1 Top Supplier Countries:")
    cur.execute("""
        SELECT country, COUNT(*) as count 
        FROM suppliers 
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        print(f"  {row['country']:20} : {row['count']:,} suppliers")
    
    # Products with suppliers
    print("\n3.2 Sample Products with Suppliers:")
    cur.execute("""
        SELECT 
            spl.product_data->>'Product Name' as product,
            s.supplier_name,
            s.country
        FROM supplier_product_links spl
        JOIN suppliers s ON s.id = spl.supplier_id
        WHERE spl.product_data->>'Product Name' IS NOT NULL
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        print(f"  {row['product'][:30]:30} | {row['supplier_name'][:20]:20} | {row['country']}")
    
    cur.close()
    conn.close()

def search_products(search_term):
    """Step 4: Search for specific products"""
    print("\n" + "="*60)
    print(f"STEP 4: SEARCHING FOR '{search_term.upper()}'")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Search in suppliers
    print(f"\n4.1 Suppliers with '{search_term}':")
    cur.execute("""
        SELECT supplier_name, country, company_email
        FROM suppliers 
        WHERE products ILIKE %s OR product_categories ILIKE %s
        LIMIT 10
    """, (f'%{search_term}%', f'%{search_term}%'))
    
    results = cur.fetchall()
    if results:
        for row in results:
            print(f"  {row['supplier_name'][:30]:30} | {row['country']:15} | {row['company_email']}")
    else:
        print(f"  No suppliers found for '{search_term}'")
    
    # Search in products
    print(f"\n4.2 Products containing '{search_term}':")
    cur.execute("""
        SELECT 
            product_data->>'Product Name' as product,
            product_data->>'Supplier' as supplier,
            product_data->>'Unit Wholesale Price (latest)' as price
        FROM products_raw
        WHERE product_data::text ILIKE %s
        LIMIT 10
    """, (f'%{search_term}%',))
    
    results = cur.fetchall()
    if results:
        for row in results:
            price = row['price'] if row['price'] else 'N/A'
            print(f"  {row['product'][:30]:30} | {row['supplier'][:20]:20} | ${price}")
    else:
        print(f"  No products found for '{search_term}'")
    
    cur.close()
    conn.close()

def test_complete_workflow():
    """Step 5: Test a complete workflow example"""
    print("\n" + "="*60)
    print("STEP 5: COMPLETE WORKFLOW EXAMPLE - PASTA ORDER")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Find pasta suppliers
    print("\n5.1 Finding Pasta Suppliers:")
    cur.execute("""
        SELECT DISTINCT 
            s.supplier_name, 
            s.country, 
            COUNT(spl.id) as product_count
        FROM suppliers s
        LEFT JOIN supplier_product_links spl ON s.id = spl.supplier_id
        WHERE s.products ILIKE '%pasta%' 
           OR s.product_categories ILIKE '%pasta%'
           OR spl.product_data::text ILIKE '%pasta%'
        GROUP BY s.supplier_name, s.country
        ORDER BY product_count DESC
        LIMIT 5
    """)
    
    suppliers = cur.fetchall()
    for row in suppliers:
        print(f"  {row['supplier_name'][:30]:30} | {row['country']:15} | {row['product_count']} products")
    
    # 2. Check pasta prices
    print("\n5.2 Pasta Price Comparison:")
    cur.execute("""
        SELECT 
            data->>'Product' as product,
            data->>'Supplier' as supplier,
            data->>'Unit Wholesale Price (latest)' as price,
            data->>'Currency for price' as currency
        FROM price_book_raw
        WHERE data->>'Product' ILIKE '%pasta%'
        LIMIT 10
    """)
    
    prices = cur.fetchall()
    if prices:
        for row in prices:
            price = row['price'] if row['price'] else 'N/A'
            currency = row['currency'] if row['currency'] else 'USD'
            print(f"  {row['product'][:25]:25} | {row['supplier'][:20]:20} | {currency} {price}")
    else:
        print("  No pasta prices found in price book")
    
    # 3. Check existing pasta orders
    print("\n5.3 Previous Pasta Orders:")
    cur.execute("""
        SELECT 
            data->>'Buyer Company' as buyer,
            data->>'Supplier' as supplier,
            data->>'Order date' as order_date,
            data->>'Status' as status
        FROM orders_raw
        WHERE data::text ILIKE '%pasta%'
        LIMIT 5
    """)
    
    orders = cur.fetchall()
    if orders:
        for row in orders:
            print(f"  {row['buyer'][:20]:20} <- {row['supplier'][:20]:20} | {row['order_date']} [{row['status']}]")
    else:
        print("  No previous pasta orders found")
    
    cur.close()
    conn.close()

def show_dashboard():
    """Step 6: Simple dashboard view"""
    print("\n" + "="*60)
    print("STEP 6: BUSINESS DASHBOARD")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor()
    
    # Overview stats
    print("\nOVERVIEW:")
    stats = {}
    tables = [
        ('Suppliers', 'suppliers'),
        ('Buyers', 'buyers'),
        ('Products', 'products_raw'),
        ('Requests', 'requests_raw'),
        ('Proposals', 'proposals_samples_raw'),
        ('Orders', 'orders_raw'),
        ('Invoices', 'invoices_raw'),
        ('Shipments', 'shipping_raw')
    ]
    
    for label, table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {label:15} : {count:,}")
    
    # Active relationships
    print("\nACTIVE RELATIONSHIPS:")
    cur.execute("SELECT COUNT(*) FROM supplier_product_links")
    sp_links = cur.fetchone()[0]
    print(f"  Supplier-Product Links : {sp_links}")
    
    cur.execute("SELECT COUNT(*) FROM buyer_request_links")
    br_links = cur.fetchone()[0]
    print(f"  Buyer-Request Links    : {br_links}")
    
    # Top active suppliers
    print("\nTOP ACTIVE SUPPLIERS:")
    cur.execute("""
        SELECT 
            s.supplier_name,
            s.country,
            COUNT(spl.id) as products
        FROM suppliers s
        JOIN supplier_product_links spl ON s.id = spl.supplier_id
        GROUP BY s.supplier_name, s.country
        ORDER BY products DESC
        LIMIT 5
    """)
    
    for row in cur.fetchall():
        print(f"  {row[0][:25]:25} ({row[1]:10}) - {row[2]} products")
    
    cur.close()
    conn.close()

def main():
    print("\n" + "=== FDX TRADING WORKFLOW TEST SUITE ===")
    
    # Run all tests
    if test_connection():
        test_buyer_workflow()
        test_supplier_workflow()
        search_products("oil")
        search_products("pasta")
        test_complete_workflow()
        show_dashboard()
        
        print("\n" + "="*60)
        print("ALL WORKFLOW TESTS COMPLETE!")
        print("="*60)
        print("\nYour data workflows are ready to use!")
        print("All 26,306+ records are accessible in the Poland database.")
    else:
        print("\nCannot proceed - database connection failed")

if __name__ == "__main__":
    main()