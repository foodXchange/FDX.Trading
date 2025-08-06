import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def analyze_table_structure(cur, table_name):
    """Analyze the structure of raw data tables"""
    print(f"\nAnalyzing {table_name}...")
    
    # Get sample data
    cur.execute(f"""
        SELECT data 
        FROM {table_name}_raw 
        LIMIT 5
    """)
    
    samples = cur.fetchall()
    if samples:
        # Parse first record to understand structure
        if isinstance(samples[0][0], dict):
            first_record = samples[0][0]
        else:
            first_record = json.loads(samples[0][0])
        print(f"  Columns found: {list(first_record.keys())}")
        
        # Get total count
        cur.execute(f"SELECT COUNT(*) FROM {table_name}_raw")
        count = cur.fetchone()[0]
        print(f"  Total records: {count}")
        
        return first_record.keys()
    return []

def create_normalized_tables(cur):
    """Create properly normalized tables with relationships"""
    print("\n=== Creating Normalized Tables with Relationships ===")
    
    # 1. Buyers table (already exists, ensure structure)
    cur.execute("""
        ALTER TABLE buyers 
        ADD COLUMN IF NOT EXISTS buyer_id TEXT UNIQUE,
        ADD COLUMN IF NOT EXISTS primary_contact TEXT,
        ADD COLUMN IF NOT EXISTS phone TEXT,
        ADD COLUMN IF NOT EXISTS address TEXT
    """)
    
    # 2. Enhanced Requests table with foreign keys
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests_normalized (
            id SERIAL PRIMARY KEY,
            request_id TEXT UNIQUE NOT NULL,
            request_number TEXT,
            buyer_id INTEGER REFERENCES buyers(id),
            buyer_name TEXT,
            status TEXT,
            request_date DATE,
            due_date DATE,
            total_items INTEGER,
            total_value DECIMAL(10,2),
            priority TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Request Line Items with relationships
    cur.execute("""
        CREATE TABLE IF NOT EXISTS request_line_items_normalized (
            id SERIAL PRIMARY KEY,
            line_item_id TEXT UNIQUE,
            request_id INTEGER REFERENCES requests_normalized(id),
            product_id INTEGER REFERENCES products(id),
            product_name TEXT,
            quantity DECIMAL(10,2),
            unit TEXT,
            target_price DECIMAL(10,2),
            specifications TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 4. Enhanced Products table
    cur.execute("""
        ALTER TABLE products 
        ADD COLUMN IF NOT EXISTS supplier_id INTEGER REFERENCES suppliers(id),
        ADD COLUMN IF NOT EXISTS category_id INTEGER,
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
        ADD COLUMN IF NOT EXISTS min_order_quantity DECIMAL(10,2),
        ADD COLUMN IF NOT EXISTS lead_time_days INTEGER
    """)
    
    # 5. Proposals with relationships
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proposals_normalized (
            id SERIAL PRIMARY KEY,
            proposal_id TEXT UNIQUE NOT NULL,
            proposal_number TEXT,
            request_id INTEGER REFERENCES requests_normalized(id),
            supplier_id INTEGER REFERENCES suppliers(id),
            supplier_name TEXT,
            status TEXT,
            proposal_date DATE,
            valid_until DATE,
            total_amount DECIMAL(10,2),
            currency TEXT DEFAULT 'USD',
            payment_terms TEXT,
            delivery_terms TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 6. Orders with complete relationships
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders_normalized (
            id SERIAL PRIMARY KEY,
            order_id TEXT UNIQUE NOT NULL,
            order_number TEXT,
            proposal_id INTEGER REFERENCES proposals_normalized(id),
            buyer_id INTEGER REFERENCES buyers(id),
            supplier_id INTEGER REFERENCES suppliers(id),
            contract_id INTEGER,
            status TEXT,
            order_date DATE,
            delivery_date DATE,
            actual_delivery_date DATE,
            total_amount DECIMAL(10,2),
            currency TEXT DEFAULT 'USD',
            payment_terms TEXT,
            payment_status TEXT,
            shipping_address TEXT,
            billing_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("  [OK] Normalized tables created with relationships")

def migrate_buyers_data(cur):
    """Migrate buyers data and assign IDs"""
    print("\n=== Migrating Buyers Data ===")
    
    # Check if we have raw data
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_name = 'buyers_raw'
    """)
    
    if cur.fetchone()[0] == 0:
        print("  No buyers_raw table found, using existing buyers table")
        # Add buyer_id if not exists
        cur.execute("""
            UPDATE buyers 
            SET buyer_id = 'BUY' || LPAD(id::text, 5, '0')
            WHERE buyer_id IS NULL
        """)
        print(f"  Updated {cur.rowcount} buyers with IDs")
    else:
        # Migrate from raw data
        cur.execute("""
            SELECT data FROM buyers_raw
        """)
        
        for row in cur.fetchall():
            # Handle both dict and string formats
            if isinstance(row[0], dict):
                data = row[0]
            else:
                data = json.loads(row[0])
            
            # Check if buyer exists
            cur.execute("""
                SELECT id FROM buyers 
                WHERE buyer_name = %s OR company_name = %s
            """, (data.get('Buyer Name', ''), data.get('Company', '')))
            
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO buyers (buyer_name, company_name, contact_email, 
                                      country, product_interests, buyer_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    data.get('Buyer Name', data.get('Name', '')),
                    data.get('Company', data.get('Company Name', '')),
                    data.get('Email', data.get('Contact Email', '')),
                    data.get('Country', ''),
                    data.get('Products', data.get('Product Interests', '')),
                    data.get('Buyer ID', f"BUY{datetime.now().strftime('%Y%m%d%H%M%S')}")
                ))
        
        print(f"  Migrated buyers data")

def migrate_requests_data(cur):
    """Migrate requests and link to buyers"""
    print("\n=== Migrating Requests Data ===")
    
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_name = 'requests_raw'
    """)
    
    if cur.fetchone()[0] == 0:
        print("  No requests_raw table found")
        return
    
    cur.execute("SELECT data FROM requests_raw")
    
    migrated = 0
    for row in cur.fetchall():
        # Handle both dict and string formats
        if isinstance(row[0], dict):
            data = row[0]
        else:
            data = json.loads(row[0])
        
        # Find matching buyer
        buyer_name = data.get('Buyer', data.get('Buyer Name', ''))
        cur.execute("""
            SELECT id FROM buyers 
            WHERE buyer_name ILIKE %s OR company_name ILIKE %s
            LIMIT 1
        """, (f"%{buyer_name}%", f"%{buyer_name}%"))
        
        buyer_result = cur.fetchone()
        buyer_id = buyer_result[0] if buyer_result else None
        
        # Insert request
        cur.execute("""
            INSERT INTO requests_normalized 
            (request_id, request_number, buyer_id, buyer_name, status, 
             request_date, due_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (request_id) DO NOTHING
        """, (
            data.get('Request ID', data.get('ID', f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}")),
            data.get('Request Number', data.get('Request #', '')),
            buyer_id,
            buyer_name,
            data.get('Status', 'Pending'),
            data.get('Request Date'),
            data.get('Due Date'),
            data.get('Notes', data.get('Description', ''))
        ))
        
        if cur.rowcount > 0:
            migrated += 1
    
    print(f"  Migrated {migrated} requests with buyer relationships")

def migrate_products_suppliers(cur):
    """Link products to suppliers"""
    print("\n=== Linking Products to Suppliers ===")
    
    # First, add supplier_id column if not exists
    cur.execute("""
        ALTER TABLE suppliers 
        ADD COLUMN IF NOT EXISTS supplier_id TEXT UNIQUE
    """)
    
    # Then ensure suppliers have proper IDs
    cur.execute("""
        UPDATE suppliers 
        SET supplier_id = 'SUP' || LPAD(id::text, 5, '0')
        WHERE supplier_id IS NULL
    """)
    
    # Check for products_raw data
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_name = 'products_raw'
    """)
    
    if cur.fetchone()[0] > 0:
        # First add product_id column if needed
        cur.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS product_id TEXT UNIQUE
        """)
        
        cur.execute("SELECT data FROM products_raw")
        
        migrated = 0
        for row in cur.fetchall():
            # Handle both dict and string formats
            if isinstance(row[0], dict):
                data = row[0]
            else:
                data = json.loads(row[0])
            
            # Find matching supplier
            supplier_name = data.get('Supplier', data.get('Supplier Name', ''))
            if supplier_name:
                cur.execute("""
                    SELECT id FROM suppliers 
                    WHERE supplier_name ILIKE %s OR company_name ILIKE %s
                    LIMIT 1
                """, (f"%{supplier_name}%", f"%{supplier_name}%"))
                
                supplier_result = cur.fetchone()
                if supplier_result:
                    
                    # Update or insert product
                    cur.execute("""
                        INSERT INTO products 
                        (product_id, product_name, supplier_id, unit_price, unit, description)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (product_id) DO UPDATE
                        SET supplier_id = EXCLUDED.supplier_id
                    """, (
                        data.get('Product ID', data.get('SKU', f"PRD{datetime.now().strftime('%Y%m%d%H%M%S')}")),
                        data.get('Product', data.get('Product Name', '')),
                        supplier_result[0],
                        data.get('Price', data.get('Unit Price')),
                        data.get('Unit', 'EA'),
                        data.get('Description', '')
                    ))
                    
                    if cur.rowcount > 0:
                        migrated += 1
        
        print(f"  Linked {migrated} products to suppliers")
    else:
        print("  No products_raw table found")

def create_relationship_views(cur):
    """Create views for easy querying of relationships"""
    print("\n=== Creating Relationship Views ===")
    
    # Buyer-Request-Supplier view
    cur.execute("""
        CREATE OR REPLACE VIEW v_buyer_requests AS
        SELECT 
            b.id as buyer_id,
            b.buyer_name,
            b.company_name as buyer_company,
            b.country as buyer_country,
            r.id as request_id,
            r.request_number,
            r.status as request_status,
            r.request_date,
            r.due_date,
            COUNT(DISTINCT p.id) as proposal_count
        FROM buyers b
        LEFT JOIN requests_normalized r ON b.id = r.buyer_id
        LEFT JOIN proposals_normalized p ON r.id = p.request_id
        GROUP BY b.id, b.buyer_name, b.company_name, b.country,
                 r.id, r.request_number, r.status, r.request_date, r.due_date
    """)
    
    # Supplier-Product-Proposal view
    cur.execute("""
        CREATE OR REPLACE VIEW v_supplier_products AS
        SELECT 
            s.id as supplier_id,
            s.supplier_name,
            s.company_name,
            s.country as supplier_country,
            COUNT(DISTINCT p.id) as product_count,
            COUNT(DISTINCT pr.id) as proposal_count,
            s.verified,
            s.rating
        FROM suppliers s
        LEFT JOIN products p ON s.id = p.supplier_id
        LEFT JOIN proposals_normalized pr ON s.id = pr.supplier_id
        GROUP BY s.id, s.supplier_name, s.company_name, s.country, s.verified, s.rating
    """)
    
    # Request fulfillment pipeline view
    cur.execute("""
        CREATE OR REPLACE VIEW v_request_pipeline AS
        SELECT 
            r.request_number,
            r.buyer_name,
            r.request_date,
            r.status as request_status,
            p.proposal_number,
            p.supplier_name,
            p.total_amount as proposal_amount,
            p.status as proposal_status,
            o.order_number,
            o.status as order_status,
            o.delivery_date
        FROM requests_normalized r
        LEFT JOIN proposals_normalized p ON r.id = p.request_id
        LEFT JOIN orders_normalized o ON p.id = o.proposal_id
        ORDER BY r.request_date DESC
    """)
    
    print("  [OK] Created 3 relationship views")

def add_performance_indexes(cur):
    """Add indexes for better query performance"""
    print("\n=== Adding Performance Indexes ===")
    
    indexes = [
        ("idx_requests_buyer", "requests_normalized(buyer_id)"),
        ("idx_proposals_request", "proposals_normalized(request_id)"),
        ("idx_proposals_supplier", "proposals_normalized(supplier_id)"),
        ("idx_products_supplier", "products(supplier_id)"),
        ("idx_orders_buyer", "orders_normalized(buyer_id)"),
        ("idx_orders_supplier", "orders_normalized(supplier_id)"),
        ("idx_orders_proposal", "orders_normalized(proposal_id)"),
        ("idx_suppliers_country", "suppliers(country)"),
        ("idx_suppliers_verified", "suppliers(verified)"),
        ("idx_buyers_country", "buyers(country)")
    ]
    
    for index_name, index_def in indexes:
        try:
            cur.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
            print(f"  [OK] Created index: {index_name}")
        except Exception as e:
            print(f"  [SKIP] Index {index_name}: {str(e)[:50]}")

def main():
    print("=" * 60)
    print("PHASE 1: IMPLEMENTING CORE RELATIONSHIPS")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(POLAND_DB)
        cur = conn.cursor()
        print("\n[OK] Connected to Poland database")
        
        # Analyze existing raw data
        tables_to_analyze = ['requests', 'products', 'proposals_samples', 'orders']
        for table in tables_to_analyze:
            try:
                analyze_table_structure(cur, table)
            except:
                pass
        
        # Create normalized tables
        create_normalized_tables(cur)
        conn.commit()
        
        # Migrate data with relationships
        migrate_buyers_data(cur)
        conn.commit()
        
        migrate_requests_data(cur)
        conn.commit()
        
        migrate_products_suppliers(cur)
        conn.commit()
        
        # Create views
        create_relationship_views(cur)
        conn.commit()
        
        # Add indexes
        add_performance_indexes(cur)
        conn.commit()
        
        # Summary
        print("\n" + "=" * 60)
        print("PHASE 1 COMPLETE!")
        print("=" * 60)
        
        # Test relationships
        print("\n=== Testing Relationships ===")
        
        cur.execute("SELECT COUNT(*) FROM v_buyer_requests")
        print(f"  Buyer-Request relationships: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM v_supplier_products WHERE product_count > 0")
        print(f"  Suppliers with products: {cur.fetchone()[0]}")
        
        cur.execute("""
            SELECT buyer_name, COUNT(*) as request_count 
            FROM v_buyer_requests 
            WHERE request_id IS NOT NULL
            GROUP BY buyer_name
            LIMIT 5
        """)
        
        print("\n  Sample Buyer-Request Relationships:")
        for row in cur.fetchall():
            print(f"    - {row[0]}: {row[1]} requests")
        
        cur.close()
        conn.close()
        
        print("\nNext steps:")
        print("1. Run: python verify_relationships.py")
        print("2. Continue with Phase 2: Product Flow")
        print("3. Build UI for relationship management")
        
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()