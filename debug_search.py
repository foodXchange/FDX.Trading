import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def test_search():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Simple query
    print("Test 1: Simple query")
    try:
        cur.execute("""
            SELECT id, supplier_name, company_name, country 
            FROM suppliers 
            LIMIT 3
        """)
        results = cur.fetchall()
        print(f"[OK] Simple query works: {len(results)} results")
    except Exception as e:
        print(f"[FAIL] Simple query failed: {e}")
    
    # Test 2: Query with products column
    print("\nTest 2: Query with products")
    try:
        cur.execute("""
            SELECT id, supplier_name, products 
            FROM suppliers 
            WHERE products IS NOT NULL
            LIMIT 3
        """)
        results = cur.fetchall()
        print(f"[OK] Products query works: {len(results)} results")
    except Exception as e:
        print(f"[FAIL] Products query failed: {e}")
    
    # Test 3: ILIKE search
    print("\nTest 3: ILIKE search")
    try:
        cur.execute("""
            SELECT id, supplier_name, company_name, country, products, 
                   supplier_type, company_email, company_website
            FROM suppliers
            WHERE products ILIKE %s
            LIMIT 5
        """, ['%oil%'])
        results = cur.fetchall()
        print(f"[OK] ILIKE search works: {len(results)} results")
    except Exception as e:
        print(f"[FAIL] ILIKE search failed: {e}")
    
    # Test 4: Text search
    print("\nTest 4: Text search")
    try:
        cur.execute("""
            SELECT id, supplier_name, company_name, country, products, 
                   supplier_type, company_email, company_website,
                   ts_rank(to_tsvector('english', products), 
                          plainto_tsquery('english', %s)) as text_score
            FROM suppliers
            WHERE to_tsvector('english', products) @@ plainto_tsquery('english', %s)
            ORDER BY text_score DESC
            LIMIT 5
        """, ['oil', 'oil'])
        results = cur.fetchall()
        print(f"[OK] Text search works: {len(results)} results")
        if results:
            print(f"  First result: {results[0]['supplier_name']}")
    except Exception as e:
        print(f"[FAIL] Text search failed: {e}")
        print(f"  Error type: {type(e).__name__}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    test_search()