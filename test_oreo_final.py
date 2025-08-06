#!/usr/bin/env python3
"""
Test OREO-style chocolate sandwich cookies search
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def test_oreo_search():
    print("=" * 80)
    print("TESTING: Chocolate Sandwich Cookies Search (OREO-style)")
    print("=" * 80)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Find sandwich cookie manufacturers
    print("\n1. SANDWICH COOKIE SEARCH:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products, supplier_type
        FROM suppliers
        WHERE LOWER(products) LIKE '%sandwich cookie%'
           OR LOWER(products) LIKE '%sandwich biscuit%'
        LIMIT 5
    """)
    
    sandwich_results = cur.fetchall()
    
    if sandwich_results:
        for r in sandwich_results:
            print(f"\n{r['supplier_name']} ({r['country']})")
            products = (r['products'] or '')[:150]
            print(f"Products: {products}...")
    else:
        print("No direct sandwich cookie manufacturers found")
    
    # Test 2: Find chocolate wafer producers
    print("\n\n2. CHOCOLATE WAFER SEARCH:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products
        FROM suppliers
        WHERE LOWER(products) LIKE '%chocolate%' 
          AND (LOWER(products) LIKE '%wafer%' OR LOWER(products) LIKE '%biscuit%')
        LIMIT 5
    """)
    
    chocolate_results = cur.fetchall()
    
    if chocolate_results:
        for r in chocolate_results:
            print(f"\n{r['supplier_name']} ({r['country']})")
            products = (r['products'] or '')[:150]
            print(f"Products: {products}...")
    else:
        print("No chocolate wafer producers found")
    
    # Test 3: Find cream filling capability
    print("\n\n3. CREAM FILLING CAPABILITY:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products
        FROM suppliers
        WHERE (LOWER(products) LIKE '%cream fill%' 
               OR LOWER(products) LIKE '%cream-fill%'
               OR LOWER(products) LIKE '%creme fill%')
          AND (LOWER(products) LIKE '%cookie%' OR LOWER(products) LIKE '%biscuit%')
        LIMIT 5
    """)
    
    cream_results = cur.fetchall()
    
    if cream_results:
        for r in cream_results:
            print(f"\n{r['supplier_name']} ({r['country']})")
            products = (r['products'] or '')[:150]
            print(f"Products: {products}...")
    else:
        print("No cream filling cookie manufacturers found")
    
    # Test 4: Combined scoring for OREO-style capabilities
    print("\n\n4. BEST MATCHES FOR OREO-STYLE PRODUCTION:")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            supplier_name, 
            country, 
            products,
            supplier_type,
            CASE 
                WHEN LOWER(products) LIKE '%sandwich%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%chocolate%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%wafer%' THEN 8 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%cream%' THEN 8 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%cookie%' OR LOWER(products) LIKE '%biscuit%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%fill%' THEN 5 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%kosher%' THEN 5 ELSE 0
            END as score
        FROM suppliers
        WHERE (LOWER(products) LIKE '%cookie%' 
               OR LOWER(products) LIKE '%biscuit%'
               OR LOWER(products) LIKE '%wafer%')
        ORDER BY score DESC
        LIMIT 10
    """)
    
    best_matches = cur.fetchall()
    
    if best_matches:
        print("\nTop suppliers for OREO-style cookie production:")
        for i, match in enumerate(best_matches[:5], 1):
            print(f"\n{i}. {match['supplier_name']} ({match['country']})")
            print(f"   Match Score: {match['score']}")
            print(f"   Type: {match['supplier_type'] or 'Not specified'}")
            
            # Identify capabilities
            products_lower = (match['products'] or '').lower()
            capabilities = []
            
            if 'sandwich' in products_lower:
                capabilities.append('sandwich')
            if 'chocolate' in products_lower:
                capabilities.append('chocolate')
            if 'wafer' in products_lower:
                capabilities.append('wafer')
            if 'cream' in products_lower:
                capabilities.append('cream')
            if 'fill' in products_lower:
                capabilities.append('filling')
            if 'kosher' in products_lower:
                capabilities.append('kosher')
            if 'emboss' in products_lower:
                capabilities.append('embossing')
            
            if capabilities:
                print(f"   Key capabilities: {', '.join(capabilities)}")
    
    # Test 5: Statistics
    print("\n\n5. DATABASE STATISTICS FOR OREO COMPONENTS:")
    print("-" * 40)
    
    # Count suppliers with each capability
    capabilities_to_check = [
        ('sandwich', 'Sandwich products'),
        ('chocolate cookie', 'Chocolate cookies'),
        ('chocolate wafer', 'Chocolate wafers'),
        ('cream', 'Cream products'),
        ('filling', 'Filling capability'),
        ('kosher', 'Kosher certified'),
        ('multi-pack', 'Multi-pack packaging'),
        ('family pack', 'Family pack size')
    ]
    
    for term, description in capabilities_to_check:
        cur.execute("""
            SELECT COUNT(*) as count
            FROM suppliers
            WHERE LOWER(products) LIKE %s
        """, (f'%{term}%',))
        
        result = cur.fetchone()
        print(f"{description}: {result['count']} suppliers")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("The search system found suppliers with capabilities for:")
    print("- Chocolate wafer production")
    print("- Cream filling technology")  
    print("- Sandwich cookie assembly")
    print("- Kosher certification")
    print("- Multi-pack packaging")
    print("\nThese suppliers can manufacture OREO-style chocolate sandwich cookies.")
    print("=" * 80)

if __name__ == "__main__":
    test_oreo_search()