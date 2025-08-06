#!/usr/bin/env python3
"""
Simple Database Efficiency Check for FDX.trading
"""

import os
import time
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def check_database_efficiency():
    print("=" * 80)
    print("DATABASE EFFICIENCY ANALYSIS FOR FDX.TRADING")
    print("=" * 80)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Basic table statistics
    print("\n1. TABLE STATISTICS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total_suppliers,
            COUNT(CASE WHEN products IS NOT NULL THEN 1 END) as with_products,
            COUNT(CASE WHEN LENGTH(products) > 500 THEN 1 END) as detailed_products,
            COUNT(CASE WHEN product_classification IS NOT NULL THEN 1 END) as classified
        FROM suppliers
    """)
    
    stats = cur.fetchone()
    print(f"Total suppliers: {stats['total_suppliers']:,}")
    print(f"With product data: {stats['with_products']:,} ({stats['with_products']*100//stats['total_suppliers']}%)")
    print(f"With detailed products: {stats['detailed_products']:,}")
    print(f"With classification: {stats['classified']:,}")
    
    # 2. Search performance tests
    print("\n2. SEARCH PERFORMANCE TESTS:")
    print("-" * 40)
    
    search_tests = [
        ("Simple search (oil)", "SELECT COUNT(*) FROM suppliers WHERE products ILIKE '%oil%'"),
        ("Complex search (chocolate wafer)", "SELECT COUNT(*) FROM suppliers WHERE products ILIKE '%chocolate%' AND products ILIKE '%wafer%'"),
        ("Country filter", "SELECT COUNT(*) FROM suppliers WHERE country IN ('USA', 'Italy', 'Spain')"),
        ("Combined search", """
            SELECT COUNT(*) FROM suppliers 
            WHERE products ILIKE '%snack%' 
            AND country = 'USA'
            AND verified = true
        """)
    ]
    
    total_time = 0
    for test_name, query in search_tests:
        start_time = time.time()
        try:
            cur.execute(query)
            result = cur.fetchone()
            execution_time = (time.time() - start_time) * 1000
            total_time += execution_time
            print(f"{test_name}: {execution_time:.2f}ms (found {result['count']} records)")
        except Exception as e:
            print(f"{test_name}: ERROR - {str(e)[:50]}")
    
    avg_time = total_time / len(search_tests)
    print(f"\nAverage query time: {avg_time:.2f}ms")
    
    if avg_time > 100:
        print("⚠️ SLOW PERFORMANCE - Optimization needed")
    elif avg_time > 50:
        print("⚠️ MODERATE PERFORMANCE - Consider optimization")
    else:
        print("✓ GOOD PERFORMANCE")
    
    # 3. Check for wafer manufacturers with variations
    print("\n3. WAFER MANUFACTURER VARIATIONS TEST:")
    print("-" * 40)
    
    start_time = time.time()
    cur.execute("""
        SELECT 
            supplier_name,
            country,
            LENGTH(products) as product_length,
            CASE WHEN products ILIKE '%strawberry%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%chocolate%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%vanilla%' THEN 1 ELSE 0 END as flavor_count,
            CASE WHEN products ILIKE '%enrob%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%coat%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%layer%' THEN 1 ELSE 0 END as capability_count
        FROM suppliers
        WHERE products ILIKE '%wafer%'
        ORDER BY (
            CASE WHEN products ILIKE '%strawberry%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%chocolate%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%vanilla%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%enrob%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%coat%' THEN 1 ELSE 0 END +
            CASE WHEN products ILIKE '%layer%' THEN 1 ELSE 0 END
        ) DESC
        LIMIT 5
    """)
    
    wafer_time = (time.time() - start_time) * 1000
    wafer_results = cur.fetchall()
    
    print(f"Wafer variation search time: {wafer_time:.2f}ms")
    print("\nTop wafer manufacturers with variations:")
    for r in wafer_results:
        total_score = r['flavor_count'] + r['capability_count']
        print(f"\n{r['supplier_name']} ({r['country']})")
        print(f"  Flavors: {r['flavor_count']}, Capabilities: {r['capability_count']}")
        print(f"  Total variation score: {total_score}")
    
    # 4. Database optimization recommendations
    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS:")
    print("=" * 80)
    
    print("\n🔴 HIGH PRIORITY:")
    print("-" * 40)
    
    print("""
1. ADD TEXT SEARCH INDEX:
   CREATE INDEX idx_suppliers_products_gin 
   ON suppliers USING gin(to_tsvector('english', products));
   
   This will speed up product searches by 10-100x
""")
    
    print("""
2. USE ILIKE INSTEAD OF LOWER() LIKE:
   Bad:  WHERE LOWER(products) LIKE '%search%'
   Good: WHERE products ILIKE '%search%'
   
   ILIKE is optimized for case-insensitive searches
""")
    
    print("\n🟡 MEDIUM PRIORITY:")
    print("-" * 40)
    
    print("""
3. ADD COUNTRY INDEX:
   CREATE INDEX idx_suppliers_country ON suppliers(country);
   
   Speeds up country-based filtering
""")
    
    print("""
4. ADD COMPOSITE INDEX FOR COMMON SEARCHES:
   CREATE INDEX idx_suppliers_search 
   ON suppliers(country, verified, rating DESC);
   
   Optimizes multi-condition queries
""")
    
    print("""
5. CREATE MATERIALIZED VIEW FOR VARIATIONS:
   CREATE MATERIALIZED VIEW supplier_variations AS
   SELECT supplier_name, country, 
          array_agg(DISTINCT flavor) as flavors,
          COUNT(DISTINCT product_type) as variation_count
   FROM suppliers
   GROUP BY supplier_name, country;
   
   Pre-calculates variation data
""")
    
    print("\n🟢 LOW PRIORITY:")
    print("-" * 40)
    
    print("""
6. PERIODIC MAINTENANCE:
   VACUUM ANALYZE suppliers;
   REINDEX TABLE suppliers;
   
   Keeps statistics updated and removes dead rows
""")
    
    # 5. Current performance summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY:")
    print("-" * 40)
    
    if avg_time < 50:
        print("✅ Database performance is GOOD")
        print("   Average query time under 50ms")
    elif avg_time < 100:
        print("⚠️ Database performance is MODERATE")
        print("   Consider implementing HIGH priority optimizations")
    else:
        print("❌ Database performance is SLOW")
        print("   Implement optimizations immediately")
    
    print(f"\nDatabase size: {stats['total_suppliers']:,} suppliers")
    print(f"Data quality: {stats['with_products']*100//stats['total_suppliers']}% have product data")
    
    # Estimate improvement potential
    print("\n📈 EXPECTED IMPROVEMENTS AFTER OPTIMIZATION:")
    print("-" * 40)
    print("• Text search: 10-100x faster with GIN index")
    print("• Country filtering: 5-10x faster with index")
    print("• Complex queries: 3-5x faster with composite indexes")
    print("• Variation searches: 20-50x faster with materialized views")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_database_efficiency()