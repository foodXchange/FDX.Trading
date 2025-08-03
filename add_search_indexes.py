#!/usr/bin/env python3
"""
Add PostgreSQL text search indexes for instant supplier queries
Keep it lean and simple - just essential indexes for performance
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def add_search_indexes():
    """Add essential text search indexes for fast supplier queries"""
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("Adding essential search indexes...")
    
    try:
        # 1. Full-text search index on products (most important)
        print("1. Creating full-text search index on products...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_suppliers_products_fts 
            ON suppliers USING gin(to_tsvector('english', products))
        """)
        
        # 2. Fast lookup indexes on common search fields
        print("2. Creating indexes on key search fields...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(supplier_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_suppliers_country ON suppliers(country)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_suppliers_type ON suppliers(supplier_type)")
        
        # 3. Composite index for filtered searches
        print("3. Creating composite index for filtered searches...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_suppliers_country_type 
            ON suppliers(country, supplier_type) 
            WHERE products IS NOT NULL
        """)
        
        # 4. Pattern matching index on supplier names (without trigram)
        print("4. Creating pattern index on supplier names...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_suppliers_name_lower 
            ON suppliers(LOWER(supplier_name))
        """)
        
        conn.commit()
        
        # Show results
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'suppliers' 
            ORDER BY indexname
        """)
        
        indexes = cur.fetchall()
        print(f"\nSuccessfully created indexes! Total: {len(indexes)}")
        for idx_name, idx_def in indexes:
            print(f"  - {idx_name}")
        
        # Test search performance
        print("\nTesting search performance...")
        
        # Test full-text search
        import time
        start = time.time()
        cur.execute("""
            SELECT COUNT(*) FROM suppliers 
            WHERE to_tsvector('english', products) @@ plainto_tsquery('english', 'oil sunflower')
        """)
        count = cur.fetchone()[0]
        duration = time.time() - start
        print(f"  Full-text search: {count} results in {duration:.3f}s")
        
        # Test filtered search
        start = time.time()
        cur.execute("""
            SELECT COUNT(*) FROM suppliers 
            WHERE country = 'Italy' AND supplier_type LIKE '%Oil%'
        """)
        count = cur.fetchone()[0]
        duration = time.time() - start
        print(f"  Filtered search: {count} results in {duration:.3f}s")
        
    except Exception as e:
        print(f"Error creating indexes: {e}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_search_indexes()
    print("\nDatabase indexing complete! Search queries will now be much faster.")