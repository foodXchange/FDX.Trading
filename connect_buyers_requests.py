import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def step1_analyze_data():
    """First, let's see what buyer names we have in requests"""
    print("\n" + "="*60)
    print("STEP 1: ANALYZING BUYER-REQUEST DATA")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get unique buyer names from requests
    print("\nBuyer names in Requests:")
    cur.execute("""
        SELECT DISTINCT data->>'Buyer' as buyer_name
        FROM requests_raw
        WHERE data->>'Buyer' IS NOT NULL
        ORDER BY buyer_name
    """)
    
    request_buyers = [row['buyer_name'] for row in cur.fetchall()]
    print(f"Found {len(request_buyers)} unique buyers in requests")
    for buyer in request_buyers[:10]:
        print(f"  - {buyer}")
    
    # Get buyer names from buyers table
    print("\nBuyer names in Buyers table:")
    cur.execute("""
        SELECT DISTINCT buyer_name, company_name
        FROM buyers
        WHERE buyer_name IS NOT NULL OR company_name IS NOT NULL
        ORDER BY buyer_name
    """)
    
    table_buyers = cur.fetchall()
    print(f"Found {len(table_buyers)} buyers in buyers table")
    for buyer in table_buyers[:10]:
        print(f"  - {buyer['buyer_name']} ({buyer['company_name']})")
    
    cur.close()
    conn.close()
    
    return request_buyers, table_buyers

def step2_create_buyer_request_table():
    """Create a proper table to link buyers and requests"""
    print("\n" + "="*60)
    print("STEP 2: CREATING BUYER-REQUEST LINK TABLE")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor()
    
    # Create the link table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyer_requests (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER REFERENCES buyers(id),
            buyer_name TEXT,
            request_id TEXT,
            request_name TEXT,
            request_date DATE,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Clear existing data for fresh start
    cur.execute("TRUNCATE TABLE buyer_requests")
    
    conn.commit()
    print("[OK] Created buyer_requests table")
    
    cur.close()
    conn.close()

def step3_link_buyers_to_requests():
    """Link buyers to their requests"""
    print("\n" + "="*60)
    print("STEP 3: LINKING BUYERS TO REQUESTS")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all requests
    cur.execute("SELECT id, data FROM requests_raw")
    requests = cur.fetchall()
    
    # Get all buyers for matching
    cur.execute("SELECT id, buyer_name, company_name FROM buyers")
    buyers = cur.fetchall()
    
    # Create buyer lookup dictionary
    buyer_lookup = {}
    for buyer in buyers:
        if buyer['buyer_name']:
            buyer_lookup[buyer['buyer_name'].lower()] = buyer['id']
        if buyer['company_name']:
            buyer_lookup[buyer['company_name'].lower()] = buyer['id']
    
    linked = 0
    unmatched_buyers = set()
    
    for request in requests:
        request_data = request['data']
        buyer_name = request_data.get('Buyer', '')
        
        if buyer_name:
            # Try to find matching buyer
            buyer_id = None
            if buyer_name.lower() in buyer_lookup:
                buyer_id = buyer_lookup[buyer_name.lower()]
            else:
                # Try partial match
                for key, bid in buyer_lookup.items():
                    if buyer_name.lower() in key or key in buyer_name.lower():
                        buyer_id = bid
                        break
            
            # Insert the link
            if buyer_id:
                cur.execute("""
                    INSERT INTO buyer_requests 
                    (buyer_id, buyer_name, request_id, request_name, request_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    buyer_id,
                    buyer_name,
                    request_data.get('Request ID'),
                    request_data.get('Request'),
                    request_data.get('Request Date'),
                    request_data.get('Request status', 'New')
                ))
                linked += 1
            else:
                unmatched_buyers.add(buyer_name)
    
    conn.commit()
    
    print(f"[OK] Linked {linked} requests to buyers")
    
    if unmatched_buyers:
        print(f"\n[WARNING] Found {len(unmatched_buyers)} unmatched buyer names:")
        for buyer in list(unmatched_buyers)[:10]:
            print(f"  - {buyer}")
        print("\nThese buyers need to be added to the buyers table")
    
    cur.close()
    conn.close()
    
    return linked, unmatched_buyers

def step4_add_missing_buyers():
    """Add missing buyers to the buyers table"""
    print("\n" + "="*60)
    print("STEP 4: ADDING MISSING BUYERS")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get unique buyers from requests that aren't in buyers table
    cur.execute("""
        SELECT DISTINCT data->>'Buyer' as buyer_name
        FROM requests_raw
        WHERE data->>'Buyer' IS NOT NULL
        AND data->>'Buyer' NOT IN (
            SELECT buyer_name FROM buyers WHERE buyer_name IS NOT NULL
            UNION
            SELECT company_name FROM buyers WHERE company_name IS NOT NULL
        )
    """)
    
    missing_buyers = cur.fetchall()
    
    added = 0
    for buyer in missing_buyers:
        if buyer['buyer_name']:
            cur.execute("""
                INSERT INTO buyers (buyer_name, company_name, verified)
                VALUES (%s, %s, FALSE)
                ON CONFLICT DO NOTHING
            """, (buyer['buyer_name'], buyer['buyer_name']))
            added += cur.rowcount
    
    conn.commit()
    print(f"[OK] Added {added} missing buyers to buyers table")
    
    cur.close()
    conn.close()
    
    return added

def step5_verify_connections():
    """Verify the connections work"""
    print("\n" + "="*60)
    print("STEP 5: VERIFYING CONNECTIONS")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check total connections
    cur.execute("SELECT COUNT(*) as total FROM buyer_requests")
    total = cur.fetchone()['total']
    print(f"\nTotal buyer-request connections: {total}")
    
    # Show sample connections
    print("\nSample Connections:")
    cur.execute("""
        SELECT 
            b.buyer_name,
            b.company_name,
            br.request_name,
            br.request_date,
            br.status
        FROM buyer_requests br
        JOIN buyers b ON b.id = br.buyer_id
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        print(f"  {row['buyer_name']:20} -> {row['request_name'][:40]:40} [{row['status']}]")
    
    # Show statistics
    print("\nStatistics:")
    cur.execute("""
        SELECT 
            COUNT(DISTINCT buyer_id) as unique_buyers,
            COUNT(DISTINCT request_id) as unique_requests
        FROM buyer_requests
    """)
    stats = cur.fetchone()
    print(f"  Unique buyers with requests: {stats['unique_buyers']}")
    print(f"  Unique requests linked: {stats['unique_requests']}")
    
    cur.close()
    conn.close()

def main():
    print("\n=== CONNECTING BUYERS TO REQUESTS ===")
    
    # Step 1: Analyze
    request_buyers, table_buyers = step1_analyze_data()
    
    # Step 2: Create table
    step2_create_buyer_request_table()
    
    # Step 3: Link data
    linked, unmatched = step3_link_buyers_to_requests()
    
    # Step 4: Add missing buyers
    if unmatched:
        added = step4_add_missing_buyers()
        # Re-link after adding missing buyers
        if added > 0:
            print("\nRe-linking with new buyers...")
            linked, unmatched = step3_link_buyers_to_requests()
    
    # Step 5: Verify
    step5_verify_connections()
    
    print("\n" + "="*60)
    print("BUYER-REQUEST CONNECTION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Connect Requests to Proposals")
    print("2. Connect Proposals to Orders")
    print("3. Build search functionality")

if __name__ == "__main__":
    main()