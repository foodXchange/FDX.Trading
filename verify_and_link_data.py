import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def verify_tables(cur):
    """Verify what tables and data we have"""
    print("\n=== Current Database State ===")
    
    # Check all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name NOT LIKE 'pg_%'
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    print(f"\nFound {len(tables)} tables:")
    
    important_tables = {}
    for table in tables:
        table_name = table[0]
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"  - {table_name}: {count:,} records")
            important_tables[table_name] = count
    
    return important_tables

def create_buyer_request_links(cur):
    """Create links between buyers and requests"""
    print("\n=== Linking Buyers to Requests ===")
    
    # Get buyers 
    cur.execute("SELECT id, buyer_name, company_name FROM buyers")
    buyers_data = cur.fetchall()
    buyers = {row[1]: row[0] for row in buyers_data}
    buyers_by_company = {row[2]: row[0] for row in buyers_data if row[2]}
    
    print(f"  Found {len(buyers)} buyers")
    
    # Process requests_raw
    updated = 0
    cur.execute("SELECT id, data FROM requests_raw")
    for row in cur.fetchall():
        if isinstance(row[1], dict):
            data = row[1]
        else:
            data = json.loads(row[1])
        
        buyer_name = data.get('Buyer', '')
        
        # Try to find buyer
        buyer_id = None
        if buyer_name in buyers:
            buyer_id = buyers[buyer_name]
        elif buyer_name in buyers_by_company:
            buyer_id = buyers_by_company[buyer_name]
        else:
            # Try partial match
            for b_name, b_id in buyers.items():
                if buyer_name and (buyer_name in b_name or b_name in buyer_name):
                    buyer_id = b_id
                    break
        
        if buyer_id:
            updated += 1
            # Store the link (we'll create a proper table for this)
    
    print(f"  Found buyer links for {updated} requests")
    return updated

def create_supplier_product_links(cur):
    """Create links between suppliers and products"""
    print("\n=== Linking Suppliers to Products ===")
    
    # Get suppliers
    cur.execute("SELECT id, supplier_name, company_name FROM suppliers LIMIT 1000")
    suppliers = {}
    for row in cur.fetchall():
        suppliers[row[1]] = row[0]
        if row[2]:
            suppliers[row[2]] = row[0]
    
    print(f"  Loaded {len(suppliers)} supplier names")
    
    # Process products_raw
    linked = 0
    cur.execute("SELECT id, data FROM products_raw")
    for row in cur.fetchall():
        if isinstance(row[1], dict):
            data = row[1]
        else:
            data = json.loads(row[1])
        
        supplier_name = data.get('Supplier', '')
        
        # Try to find supplier
        supplier_id = None
        if supplier_name in suppliers:
            supplier_id = suppliers[supplier_name]
            linked += 1
    
    print(f"  Found supplier links for {linked} products")
    return linked

def create_link_tables(cur):
    """Create simplified link tables"""
    print("\n=== Creating Link Tables ===")
    
    # Buyer-Request links
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyer_request_links (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER REFERENCES buyers(id),
            request_raw_id INTEGER,
            request_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Supplier-Product links
    cur.execute("""
        CREATE TABLE IF NOT EXISTS supplier_product_links (
            id SERIAL PRIMARY KEY,
            supplier_id INTEGER REFERENCES suppliers(id),
            product_raw_id INTEGER,
            product_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Request-Proposal links
    cur.execute("""
        CREATE TABLE IF NOT EXISTS request_proposal_links (
            id SERIAL PRIMARY KEY,
            request_raw_id INTEGER,
            proposal_raw_id INTEGER,
            supplier_id INTEGER REFERENCES suppliers(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("  [OK] Link tables created")

def populate_buyer_request_links(cur):
    """Populate the buyer-request link table"""
    print("\n=== Populating Buyer-Request Links ===")
    
    # Get buyers
    cur.execute("SELECT id, buyer_name, company_name FROM buyers")
    buyers_list = cur.fetchall()
    
    # Process each request
    cur.execute("SELECT id, data FROM requests_raw")
    requests = cur.fetchall()
    
    linked = 0
    for req_id, req_data in requests:
        if isinstance(req_data, dict):
            data = req_data
        else:
            data = json.loads(req_data)
        
        buyer_name = str(data.get('Buyer', '') or '').strip()
        
        # Find matching buyer
        for buyer_id, b_name, b_company in buyers_list:
            if (buyer_name and 
                (buyer_name.lower() == b_name.lower() or 
                 buyer_name.lower() == b_company.lower() or
                 buyer_name.lower() in b_name.lower() or
                 buyer_name.lower() in b_company.lower())):
                
                cur.execute("""
                    INSERT INTO buyer_request_links (buyer_id, request_raw_id, request_data)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (buyer_id, req_id, json.dumps(data)))
                
                linked += 1
                break
    
    print(f"  Created {linked} buyer-request links")
    return linked

def populate_supplier_product_links(cur):
    """Populate the supplier-product link table"""
    print("\n=== Populating Supplier-Product Links ===")
    
    # Process products
    cur.execute("SELECT id, data FROM products_raw")
    products = cur.fetchall()
    
    linked = 0
    for prod_id, prod_data in products:
        if isinstance(prod_data, dict):
            data = prod_data
        else:
            data = json.loads(prod_data)
        
        supplier_name = str(data.get('Supplier', '') or '').strip()
        
        if supplier_name:
            # Find matching supplier
            cur.execute("""
                SELECT id FROM suppliers 
                WHERE supplier_name ILIKE %s OR company_name ILIKE %s
                LIMIT 1
            """, (supplier_name, supplier_name))
            
            supplier = cur.fetchone()
            if supplier:
                cur.execute("""
                    INSERT INTO supplier_product_links (supplier_id, product_raw_id, product_data)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (supplier[0], prod_id, json.dumps(data)))
                
                linked += 1
    
    print(f"  Created {linked} supplier-product links")
    return linked

def create_summary_views(cur):
    """Create views to see the relationships"""
    print("\n=== Creating Summary Views ===")
    
    # Buyer activity view
    cur.execute("""
        CREATE OR REPLACE VIEW v_buyer_activity AS
        SELECT 
            b.id,
            b.buyer_name,
            b.company_name,
            b.country,
            COUNT(DISTINCT brl.request_raw_id) as request_count,
            MIN(brl.request_data->>'Request Date') as first_request,
            MAX(brl.request_data->>'Request Date') as last_request
        FROM buyers b
        LEFT JOIN buyer_request_links brl ON b.id = brl.buyer_id
        GROUP BY b.id, b.buyer_name, b.company_name, b.country
    """)
    
    # Supplier catalog view
    cur.execute("""
        CREATE OR REPLACE VIEW v_supplier_catalog AS
        SELECT 
            s.id,
            s.supplier_name,
            s.country,
            COUNT(DISTINCT spl.product_raw_id) as product_count,
            STRING_AGG(DISTINCT spl.product_data->>'Product Name', ', ' 
                      ORDER BY spl.product_data->>'Product Name') as sample_products
        FROM suppliers s
        LEFT JOIN supplier_product_links spl ON s.id = spl.supplier_id
        GROUP BY s.id, s.supplier_name, s.country
        HAVING COUNT(DISTINCT spl.product_raw_id) > 0
    """)
    
    print("  [OK] Summary views created")

def main():
    print("=" * 60)
    print("VERIFYING AND LINKING BUSINESS DATA")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(POLAND_DB)
        cur = conn.cursor()
        print("\n[OK] Connected to Poland database")
        
        # Verify current state
        tables = verify_tables(cur)
        
        # Create link tables
        create_link_tables(cur)
        conn.commit()
        
        # Check what we can link
        if 'buyers' in tables and 'requests_raw' in tables:
            create_buyer_request_links(cur)
        
        if 'suppliers' in tables and 'products_raw' in tables:
            create_supplier_product_links(cur)
        
        # Populate links
        if 'requests_raw' in tables:
            populate_buyer_request_links(cur)
            conn.commit()
        
        if 'products_raw' in tables:
            populate_supplier_product_links(cur)
            conn.commit()
        
        # Create views
        create_summary_views(cur)
        conn.commit()
        
        # Show summary
        print("\n" + "=" * 60)
        print("LINKING COMPLETE!")
        print("=" * 60)
        
        # Test the views
        print("\n=== Testing Relationships ===")
        
        cur.execute("SELECT COUNT(*) FROM v_buyer_activity WHERE request_count > 0")
        active_buyers = cur.fetchone()[0]
        print(f"  Active buyers (with requests): {active_buyers}")
        
        cur.execute("SELECT COUNT(*) FROM v_supplier_catalog")
        suppliers_with_products = cur.fetchone()[0]
        print(f"  Suppliers with products: {suppliers_with_products}")
        
        # Show samples
        print("\n  Top Buyers by Request Count:")
        cur.execute("""
            SELECT buyer_name, company_name, request_count 
            FROM v_buyer_activity 
            WHERE request_count > 0
            ORDER BY request_count DESC 
            LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"    - {row[0]} ({row[1]}): {row[2]} requests")
        
        print("\n  Sample Suppliers with Products:")
        cur.execute("""
            SELECT supplier_name, country, product_count, 
                   SUBSTRING(sample_products, 1, 100) as products
            FROM v_supplier_catalog 
            ORDER BY product_count DESC 
            LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"    - {row[0]} ({row[1]}): {row[2]} products")
            print(f"      Products: {row[3]}...")
        
        cur.close()
        conn.close()
        
        print("\n[OK] Data relationships established!")
        print("\nNext steps:")
        print("1. Review the link tables to verify accuracy")
        print("2. Create dashboards using the views")
        print("3. Build APIs to query relationships")
        
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()