#!/usr/bin/env python3
"""
Complete Cache Optimization - Fill remaining suppliers
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def complete_cache():
    print("=" * 80)
    print("COMPLETING SEARCH CACHE OPTIMIZATION")
    print("=" * 80)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Get uncached suppliers
    print("\n1. Finding uncached suppliers...")
    cur.execute("""
        SELECT COUNT(*) FROM suppliers s
        WHERE NOT EXISTS (
            SELECT 1 FROM supplier_search_keywords k 
            WHERE k.supplier_id = s.id
        )
    """)
    uncached = cur.fetchone()[0]
    print(f"Suppliers not in cache: {uncached:,}")
    
    if uncached == 0:
        print("All suppliers already cached!")
        return
    
    # Add remaining suppliers
    print("\n2. Adding remaining suppliers to cache...")
    print("This will take 2-3 minutes...")
    
    # Common keywords to extract
    keywords = ['oil', 'chocolate', 'wafer', 'biscuit', 'cookie', 'snack', 
                'puff', 'corn', 'cheese', 'cream', 'sandwich', 'pasta', 
                'rice', 'flour', 'sugar', 'dairy', 'meat', 'fruit', 
                'vegetable', 'nuts', 'organic', 'kosher', 'halal']
    
    batch_count = 0
    for keyword in keywords:
        # Find suppliers with this keyword not yet cached
        cur.execute("""
            INSERT INTO supplier_search_keywords (supplier_id, keyword, keyword_type, weight)
            SELECT DISTINCT s.id, %s, 'product', 10
            FROM suppliers s
            WHERE (LOWER(s.products) LIKE '%%' || %s || '%%' 
                   OR LOWER(s.supplier_name) LIKE '%%' || %s || '%%')
            AND NOT EXISTS (
                SELECT 1 FROM supplier_search_keywords k 
                WHERE k.supplier_id = s.id AND k.keyword = %s
            )
            ON CONFLICT (supplier_id, keyword) DO NOTHING
        """, (keyword, keyword, keyword, keyword))
        
        added = cur.rowcount
        if added > 0:
            batch_count += added
            print(f"  Added '{keyword}': {added} suppliers")
        
        if batch_count > 1000:
            conn.commit()
            batch_count = 0
    
    conn.commit()
    
    # Final stats
    print("\n3. OPTIMIZATION COMPLETE!")
    print("-" * 40)
    
    cur.execute("SELECT COUNT(DISTINCT supplier_id) FROM supplier_search_keywords")
    cached = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM suppliers")
    total = cur.fetchone()[0]
    
    print(f"Total suppliers: {total:,}")
    print(f"Suppliers in cache: {cached:,}")
    print(f"Cache coverage: {cached*100//total}%")
    
    # Test performance
    print("\n4. Performance test:")
    import time
    
    start = time.time()
    cur.execute("""
        SELECT COUNT(DISTINCT supplier_id) 
        FROM supplier_search_keywords 
        WHERE keyword IN ('chocolate', 'wafer')
    """)
    result = cur.fetchone()[0]
    elapsed = (time.time() - start) * 1000
    
    print(f"Multi-keyword search: {elapsed:.1f}ms ({result} results)")
    print("Status: OPTIMIZED!" if elapsed < 50 else "Status: Good")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    complete_cache()