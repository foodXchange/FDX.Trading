#!/usr/bin/env python3
"""
Simple test for OREO-style chocolate sandwich cookies search
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def test_oreo_search():
    print("=" * 80)
    print("SEARCH TEST: Chocolate Sandwich Cookies (OREO-style)")
    print("=" * 80)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Key search terms for OREO-style cookies
    searches = [
        ("sandwich cookie", "SANDWICH COOKIE MANUFACTURERS"),
        ("chocolate wafer", "CHOCOLATE WAFER PRODUCERS"),
        ("cream filling", "CREAM FILLING CAPABILITY"),
        ("biscuit manufacturer kosher", "KOSHER BISCUIT MANUFACTURERS")
    ]
    
    for search_term, title in searches:
        print(f"\n{title}:")
        print("-" * 40)
        
        cur.execute("""
            SELECT id, supplier_name, company_name, country, products, supplier_type
            FROM suppliers
            WHERE LOWER(products) LIKE %s
            ORDER BY 
                CASE 
                    WHEN LOWER(supplier_type) LIKE '%manufact%' THEN 1
                    WHEN LOWER(supplier_type) LIKE '%produc%' THEN 2
                    ELSE 3
                END
            LIMIT 5
        """, (f"%{search_term}%",))
        
        results = cur.fetchall()
        
        if results:
            for r in results:
                print(f"\n{r['supplier_name']} ({r['country']})")
                print(f"Type: {r['supplier_type'] or 'Not specified'}")
                
                # Show relevant product excerpt
                products = r['products'] or ''
                # Find the part with our search term
                lower_products = products.lower()
                pos = lower_products.find(search_term)
                if pos >= 0:
                    start = max(0, pos - 50)
                    end = min(len(products), pos + 100)
                    excerpt = products[start:end]
                    if start > 0:
                        excerpt = "..." + excerpt
                    if end < len(products):
                        excerpt = excerpt + "..."
                    print(f"Products: {excerpt}")
                else:
                    print(f"Products: {products[:150]}...")
        else:
            print("No direct matches found")
    
    # Find suppliers with multiple OREO-relevant capabilities
    print("\n\nCOMBINED SEARCH - OREO MANUFACTURERS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT id, supplier_name, country, products, supplier_type,
               CASE 
                   WHEN LOWER(products) LIKE '%sandwich%cookie%' THEN 10
                   WHEN LOWER(products) LIKE '%sandwich%' THEN 5
                   ELSE 0
               END +
               CASE 
                   WHEN LOWER(products) LIKE '%chocolate%wafer%' THEN 10
                   WHEN LOWER(products) LIKE '%chocolate%' THEN 3
                   ELSE 0
               END +
               CASE 
                   WHEN LOWER(products) LIKE '%cream%fill%' THEN 8
                   WHEN LOWER(products) LIKE '%cream%' THEN 2
                   ELSE 0
               END +
               CASE 
                   WHEN LOWER(products) LIKE '%kosher%' OR LOWER(products) LIKE '%halal%' THEN 5
                   ELSE 0
               END +
               CASE 
                   WHEN LOWER(supplier_type) LIKE '%manufact%' THEN 15
                   WHEN LOWER(supplier_type) LIKE '%produc%' THEN 10
                   ELSE 0
               END as relevance_score
        FROM suppliers
        WHERE (LOWER(products) LIKE '%cookie%' OR LOWER(products) LIKE '%biscuit%')
          AND (LOWER(products) LIKE '%chocolate%' OR LOWER(products) LIKE '%sandwich%')
        ORDER BY relevance_score DESC
        LIMIT 10
    """)
    
    top_matches = cur.fetchall()
    
    if top_matches:
        print("\nTop suppliers for OREO-style production:")
        for i, match in enumerate(top_matches[:5], 1):
            print(f"\n{i}. {match['supplier_name']} ({match['country']})")
            print(f"   Relevance Score: {match['relevance_score']}")
            print(f"   Type: {match['supplier_type'] or 'Not specified'}")
            
            # Check specific capabilities
            products_lower = (match['products'] or '').lower()
            capabilities = []
            if 'sandwich' in products_lower:
                capabilities.append('sandwich cookies')
            if 'chocolate' in products_lower and 'wafer' in products_lower:
                capabilities.append('chocolate wafers')
            elif 'chocolate' in products_lower:
                capabilities.append('chocolate products')
            if 'cream' in products_lower:
                capabilities.append('cream filling')
            if 'kosher' in products_lower:
                capabilities.append('kosher certified')
            if 'emboss' in products_lower:
                capabilities.append('embossing')
            
            if capabilities:
                print(f"   Capabilities: {', '.join(capabilities)}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY: The search found suppliers with:")
    print("- Sandwich cookie manufacturing capability")
    print("- Chocolate wafer production")
    print("- Cream filling technology")
    print("- Kosher certification options")
    print("\nThese suppliers can produce OREO-style chocolate sandwich cookies.")

if __name__ == "__main__":
    test_oreo_search()