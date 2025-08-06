#!/usr/bin/env python3
"""
Database Efficiency Check and Optimization Suggestions for FDX.trading
Analyzes current database performance and suggests optimizations
"""

import os
import time
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def check_database_efficiency():
    """Comprehensive database efficiency analysis"""
    
    print("=" * 80)
    print("DATABASE EFFICIENCY ANALYSIS FOR FDX.TRADING")
    print("=" * 80)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Check table sizes and row counts
    print("\n1. TABLE SIZES AND ROW COUNTS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
            n_live_tup as row_count
        FROM pg_stat_user_tables
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 10
    """)
    
    tables = cur.fetchall()
    for table in tables:
        print(f"{table['tablename']}: {table['size']} ({table['row_count']:,} rows)")
    
    # 2. Check existing indexes
    print("\n2. EXISTING INDEXES:")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname
    """)
    
    indexes = cur.fetchall()
    current_table = None
    for idx in indexes[:20]:  # Show first 20
        if idx['tablename'] != current_table:
            print(f"\nTable: {idx['tablename']}")
            current_table = idx['tablename']
        print(f"  - {idx['indexname']}")
    
    # 3. Check slow queries (if pg_stat_statements available)
    print("\n3. QUERY PERFORMANCE ANALYSIS:")
    print("-" * 40)
    
    # Test common search patterns performance
    search_tests = [
        ("Simple product search", "SELECT COUNT(*) FROM suppliers WHERE LOWER(products) LIKE '%oil%'"),
        ("Multiple condition search", """
            SELECT COUNT(*) FROM suppliers 
            WHERE LOWER(products) LIKE '%chocolate%' 
            AND LOWER(products) LIKE '%wafer%'
        """),
        ("Complex scoring search", """
            SELECT COUNT(*) FROM suppliers 
            WHERE (LOWER(products) LIKE '%puff%' OR LOWER(products) LIKE '%snack%')
            AND country IN ('USA', 'Italy', 'Spain')
        """)
    ]
    
    for test_name, query in search_tests:
        start_time = time.time()
        cur.execute(query)
        result = cur.fetchone()
        execution_time = (time.time() - start_time) * 1000
        print(f"{test_name}: {execution_time:.2f}ms (found {result['count']} records)")
    
    # 4. Check for missing indexes on frequently searched columns
    print("\n4. MISSING INDEX ANALYSIS:")
    print("-" * 40)
    
    # Check if important columns have indexes
    important_columns = [
        ('suppliers', 'products'),
        ('suppliers', 'country'),
        ('suppliers', 'supplier_type'),
        ('suppliers', 'verified'),
        ('suppliers', 'rating'),
        ('suppliers', 'product_classification')
    ]
    
    for table, column in important_columns:
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE tablename = %s 
            AND indexdef LIKE %s
        """, (table, f'%{column}%'))
        
        result = cur.fetchone()
        if result['count'] == 0:
            print(f"⚠️ Missing index on {table}.{column}")
        else:
            print(f"✓ Index exists on {table}.{column}")
    
    # 5. Check table statistics
    print("\n5. TABLE STATISTICS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            schemaname,
            tablename,
            n_dead_tup,
            n_live_tup,
            CASE 
                WHEN n_live_tup > 0 
                THEN ROUND(100.0 * n_dead_tup / n_live_tup, 2)
                ELSE 0
            END as dead_tuple_percent,
            last_vacuum,
            last_autovacuum
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY n_dead_tup DESC
        LIMIT 5
    """)
    
    stats = cur.fetchall()
    for stat in stats:
        print(f"{stat['tablename']}:")
        print(f"  Dead tuples: {stat['n_dead_tup']:,} ({stat['dead_tuple_percent']}%)")
        print(f"  Last vacuum: {stat['last_vacuum'] or 'Never'}")
        print(f"  Last autovacuum: {stat['last_autovacuum'] or 'Never'}")
    
    # 6. Generate optimization recommendations
    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS:")
    print("=" * 80)
    
    recommendations = []
    
    # Check if text search indexes are needed
    cur.execute("""
        SELECT COUNT(*) FROM pg_indexes 
        WHERE indexdef LIKE '%gin%' 
        AND tablename = 'suppliers'
    """)
    gin_count = cur.fetchone()['count']
    
    if gin_count == 0:
        recommendations.append({
            'priority': 'HIGH',
            'type': 'INDEX',
            'description': 'Add GIN index for full-text search on products',
            'sql': """
                CREATE INDEX idx_suppliers_products_gin 
                ON suppliers USING gin(to_tsvector('english', products));
            """
        })
    
    # Check for missing B-tree indexes
    cur.execute("""
        SELECT COUNT(*) FROM pg_indexes 
        WHERE tablename = 'suppliers' 
        AND indexname LIKE '%country%'
    """)
    country_idx = cur.fetchone()['count']
    
    if country_idx == 0:
        recommendations.append({
            'priority': 'MEDIUM',
            'type': 'INDEX',
            'description': 'Add index on country column for faster filtering',
            'sql': "CREATE INDEX idx_suppliers_country ON suppliers(country);"
        })
    
    # Check for composite indexes
    recommendations.append({
        'priority': 'MEDIUM',
        'type': 'INDEX',
        'description': 'Add composite index for common search patterns',
        'sql': """
            CREATE INDEX idx_suppliers_search_composite 
            ON suppliers(country, verified, rating DESC);
        """
    })
    
    # Suggest partitioning for large tables
    cur.execute("SELECT COUNT(*) FROM suppliers")
    supplier_count = cur.fetchone()['count']
    
    if supplier_count > 100000:
        recommendations.append({
            'priority': 'LOW',
            'type': 'PARTITION',
            'description': f'Consider partitioning suppliers table ({supplier_count:,} rows)',
            'sql': "Consider partitioning by country or creation date"
        })
    
    # Suggest materialized views for complex queries
    recommendations.append({
        'priority': 'MEDIUM',
        'type': 'MATERIALIZED VIEW',
        'description': 'Create materialized view for product variations',
        'sql': """
            CREATE MATERIALIZED VIEW supplier_product_variations AS
            SELECT 
                supplier_name,
                country,
                COUNT(DISTINCT 
                    CASE 
                        WHEN products LIKE '%strawberry%' THEN 'strawberry'
                        WHEN products LIKE '%chocolate%' THEN 'chocolate'
                        WHEN products LIKE '%vanilla%' THEN 'vanilla'
                    END
                ) as flavor_count,
                products
            FROM suppliers
            GROUP BY supplier_name, country, products;
        """
    })
    
    # Suggest query optimization
    recommendations.append({
        'priority': 'HIGH',
        'type': 'QUERY',
        'description': 'Use ILIKE instead of LOWER() LIKE for case-insensitive search',
        'sql': "Change: LOWER(products) LIKE '%search%' TO: products ILIKE '%search%'"
    })
    
    # Print recommendations
    print("\nRECOMMENDED OPTIMIZATIONS:")
    print("-" * 40)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec['priority']}] {rec['type']}: {rec['description']}")
        if rec['sql']:
            print(f"   SQL: {rec['sql'][:100]}...")
    
    # 7. Test wafer search with proper query
    print("\n\n7. OPTIMIZED WAFER SEARCH TEST:")
    print("-" * 40)
    
    # Fixed query for wafer variations
    cur.execute("""
        WITH wafer_suppliers AS (
            SELECT 
                supplier_name,
                country,
                products,
                supplier_type,
                (CASE WHEN products ILIKE '%strawberry%' THEN 1 ELSE 0 END +
                 CASE WHEN products ILIKE '%chocolate%' THEN 1 ELSE 0 END +
                 CASE WHEN products ILIKE '%vanilla%' THEN 1 ELSE 0 END) as flavors,
                (CASE WHEN products ILIKE '%enrob%' THEN 1 ELSE 0 END +
                 CASE WHEN products ILIKE '%layer%' THEN 1 ELSE 0 END +
                 CASE WHEN products ILIKE '%cream%' THEN 1 ELSE 0 END) as capabilities
            FROM suppliers
            WHERE products ILIKE '%wafer%'
        )
        SELECT 
            supplier_name,
            country,
            flavors,
            capabilities,
            (flavors + capabilities) as total_score
        FROM wafer_suppliers
        ORDER BY total_score DESC
        LIMIT 5
    """)
    
    wafer_results = cur.fetchall()
    
    print("Top wafer manufacturers with variations:")
    for r in wafer_results:
        print(f"\n{r['supplier_name']} ({r['country']})")
        print(f"  Flavor variations: {r['flavors']}")
        print(f"  Production capabilities: {r['capabilities']}")
        print(f"  Total variation score: {r['total_score']}")
    
    # 8. Performance summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY:")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total_suppliers,
            COUNT(CASE WHEN products IS NOT NULL THEN 1 END) as with_products,
            COUNT(CASE WHEN LENGTH(products) > 500 THEN 1 END) as detailed_products,
            AVG(LENGTH(products)) as avg_product_length
        FROM suppliers
    """)
    
    summary = cur.fetchone()
    
    print(f"Total suppliers: {summary['total_suppliers']:,}")
    print(f"With product data: {summary['with_products']:,}")
    print(f"With detailed products (>500 chars): {summary['detailed_products']:,}")
    print(f"Average product description length: {summary['avg_product_length']:.0f} chars")
    
    # Calculate search efficiency
    print("\nSEARCH EFFICIENCY METRICS:")
    start = time.time()
    cur.execute("SELECT COUNT(*) FROM suppliers WHERE products ILIKE '%wafer%'")
    wafer_time = (time.time() - start) * 1000
    
    start = time.time()
    cur.execute("SELECT COUNT(*) FROM suppliers WHERE products ILIKE '%chocolate%' AND products ILIKE '%wafer%'")
    complex_time = (time.time() - start) * 1000
    
    print(f"Simple search (wafer): {wafer_time:.2f}ms")
    print(f"Complex search (chocolate wafer): {complex_time:.2f}ms")
    
    if complex_time > 100:
        print("⚠️ Complex searches are slow - implement recommended indexes")
    else:
        print("✓ Search performance is acceptable")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("OPTIMIZATION PRIORITY:")
    print("-" * 40)
    print("1. IMMEDIATE: Add GIN index for text search")
    print("2. HIGH: Switch to ILIKE for case-insensitive searches")
    print("3. MEDIUM: Add indexes on country, supplier_type")
    print("4. MEDIUM: Create materialized views for complex aggregations")
    print("5. LOW: Consider partitioning if data grows beyond 100K rows")
    print("=" * 80)

if __name__ == "__main__":
    check_database_efficiency()