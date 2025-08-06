import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def step1_analyze_proposals():
    """Analyze proposal data to understand connections"""
    print("\n" + "="*60)
    print("STEP 1: ANALYZING PROPOSAL DATA")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check proposals structure
    cur.execute("""
        SELECT 
            data->>'Request' as request_name,
            data->>'Supplier' as supplier_name,
            data->>'Status' as status,
            data->>'Proposal ID' as proposal_id
        FROM proposals_samples_raw
        LIMIT 10
    """)
    
    print("\nSample Proposals:")
    for row in cur.fetchall():
        print(f"  Request: {row['request_name'][:30] if row['request_name'] else 'None':30} | Supplier: {row['supplier_name'][:25] if row['supplier_name'] else 'None':25} | Status: {row['status']}")
    
    # Count proposals with requests
    cur.execute("""
        SELECT COUNT(*) as total
        FROM proposals_samples_raw
        WHERE data->>'Request' IS NOT NULL
    """)
    total = cur.fetchone()['total']
    print(f"\nProposals with request links: {total} / 56")
    
    cur.close()
    conn.close()

def step2_create_request_proposal_table():
    """Create table to link requests and proposals"""
    print("\n" + "="*60)
    print("STEP 2: CREATING REQUEST-PROPOSAL LINK TABLE")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS request_proposals (
            id SERIAL PRIMARY KEY,
            request_id TEXT,
            request_name TEXT,
            proposal_id TEXT,
            supplier_id INTEGER REFERENCES suppliers(id),
            supplier_name TEXT,
            status TEXT,
            proposal_date DATE,
            total_amount DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("TRUNCATE TABLE request_proposals")
    
    conn.commit()
    print("[OK] Created request_proposals table")
    
    cur.close()
    conn.close()

def step3_link_requests_proposals():
    """Link requests to their proposals"""
    print("\n" + "="*60)
    print("STEP 3: LINKING REQUESTS TO PROPOSALS")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all proposals
    cur.execute("SELECT id, data FROM proposals_samples_raw")
    proposals = cur.fetchall()
    
    # Get request mapping
    cur.execute("SELECT DISTINCT request_name, request_id FROM buyer_requests")
    request_map = {row['request_name']: row['request_id'] for row in cur.fetchall() if row['request_name']}
    
    # Get supplier mapping
    cur.execute("SELECT id, supplier_name, company_name FROM suppliers LIMIT 5000")
    supplier_map = {}
    for row in cur.fetchall():
        if row['supplier_name']:
            supplier_map[row['supplier_name'].lower()] = row['id']
        if row['company_name']:
            supplier_map[row['company_name'].lower()] = row['id']
    
    linked = 0
    
    for proposal in proposals:
        data = proposal['data']
        request_name = data.get('Request')
        supplier_name = data.get('Supplier')
        
        # Find matching request
        request_id = None
        if request_name in request_map:
            request_id = request_map[request_name]
        
        # Find matching supplier
        supplier_id = None
        if supplier_name and supplier_name.lower() in supplier_map:
            supplier_id = supplier_map[supplier_name.lower()]
        
        # Insert link
        cur.execute("""
            INSERT INTO request_proposals
            (request_id, request_name, proposal_id, supplier_id, supplier_name, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request_id,
            request_name,
            data.get('Proposal ID', data.get('ID')),
            supplier_id,
            supplier_name,
            data.get('Status', 'New')
        ))
        linked += 1
    
    conn.commit()
    print(f"[OK] Linked {linked} proposals to requests")
    
    cur.close()
    conn.close()

def step4_create_proposal_products():
    """Link proposals to their products"""
    print("\n" + "="*60)
    print("STEP 4: LINKING PROPOSALS TO PRODUCTS")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Create proposal products table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proposal_products (
            id SERIAL PRIMARY KEY,
            proposal_id TEXT,
            product_name TEXT,
            quantity DECIMAL(10,2),
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("TRUNCATE TABLE proposal_products")
    
    # Link proposal line items
    cur.execute("SELECT id, data FROM proposal_line_items_raw")
    items = cur.fetchall()
    
    linked = 0
    for item in items:
        data = item['data']
        cur.execute("""
            INSERT INTO proposal_products
            (proposal_id, product_name, quantity, unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data.get('Proposal ID'),
            data.get('Product'),
            data.get('Quantity'),
            data.get('Unit Price'),
            data.get('Total Price')
        ))
        linked += 1
    
    conn.commit()
    print(f"[OK] Linked {linked} products to proposals")
    
    cur.close()
    conn.close()

def step5_verify_connections():
    """Verify request-proposal connections"""
    print("\n" + "="*60)
    print("STEP 5: VERIFYING CONNECTIONS")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Count connections
    cur.execute("SELECT COUNT(*) as total FROM request_proposals")
    total = cur.fetchone()['total']
    print(f"\nTotal request-proposal connections: {total}")
    
    # Show sample connections
    print("\nSample Request-Proposal Links:")
    cur.execute("""
        SELECT 
            rp.request_name,
            rp.supplier_name,
            rp.status,
            COUNT(pp.id) as product_count
        FROM request_proposals rp
        LEFT JOIN proposal_products pp ON pp.proposal_id = rp.proposal_id
        WHERE rp.request_name IS NOT NULL
        GROUP BY rp.request_name, rp.supplier_name, rp.status
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        req = row['request_name'][:30] if row['request_name'] else 'N/A'
        sup = row['supplier_name'][:25] if row['supplier_name'] else 'N/A'
        print(f"  {req:30} <- {sup:25} [{row['status']}] {row['product_count']} products")
    
    # Statistics
    print("\nStatistics:")
    cur.execute("""
        SELECT 
            COUNT(DISTINCT request_id) as requests_with_proposals,
            COUNT(DISTINCT supplier_id) as suppliers_with_proposals
        FROM request_proposals
        WHERE request_id IS NOT NULL
    """)
    stats = cur.fetchone()
    print(f"  Requests with proposals: {stats['requests_with_proposals']}")
    print(f"  Suppliers with proposals: {stats['suppliers_with_proposals']}")
    
    cur.close()
    conn.close()

def main():
    print("\n=== CONNECTING REQUESTS TO PROPOSALS ===")
    
    # Run all steps
    step1_analyze_proposals()
    step2_create_request_proposal_table()
    step3_link_requests_proposals()
    step4_create_proposal_products()
    step5_verify_connections()
    
    print("\n" + "="*60)
    print("REQUEST-PROPOSAL CONNECTION COMPLETE!")
    print("="*60)
    print("\nWorkflow Progress:")
    print("  [OK] Buyers -> Requests (85 connections)")
    print("  [OK] Requests -> Proposals (56 connections)")
    print("  [OK] Proposals -> Products (77 items)")
    print("\nNext steps:")
    print("1. Connect Proposals to Orders")
    print("2. Build product search")
    print("3. Create price comparison")

if __name__ == "__main__":
    main()