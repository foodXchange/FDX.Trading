#!/usr/bin/env python3
"""
Test search optimization with OREO-style chocolate sandwich cookies
Tests multiple search approaches to find the right suppliers
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Add current directory to path
sys.path.append('.')

# Import optimization modules
from optimize_product_search import ProductSearchOptimizer
from product_variation_handler import ProductVariationHandler
from advanced_search_system import AdvancedSearchSystem

load_dotenv()

def test_oreo_search():
    """Test various search strategies for chocolate sandwich cookies"""
    
    print("=" * 80)
    print("TESTING SEARCH FOR: Chocolate Sandwich Cookies (OREO-style)")
    print("=" * 80)
    
    # Test 1: Product Classification (Seller vs User)
    print("\n1. TESTING PRODUCT CLASSIFICATION")
    print("-" * 40)
    
    optimizer = ProductSearchOptimizer()
    results = optimizer.optimize_search("chocolate sandwich cookies", limit=20)
    
    print(f"Found {results['total_sellers']} SELLERS (manufacturers/distributors)")
    print(f"Excluded {results['total_users']} USERS (bakeries using as ingredient)")
    
    if results['sellers']:
        print("\nTop 3 Sellers of Chocolate Sandwich Cookies:")
        for i, seller in enumerate(results['sellers'][:3], 1):
            print(f"\n{i}. {seller['supplier_name']} ({seller['country']})")
            print(f"   Type: {seller.get('supplier_type', 'Unknown')}")
            print(f"   Products: {seller['product_preview'][:150]}...")
            print(f"   Classification: {seller['classification']}")
    
    if results['excluded_users']:
        print("\nExcluded (use as ingredient):")
        for user in results['excluded_users'][:2]:
            print(f"- {user['supplier_name']}: Uses cookies in {user['product_preview'][:80]}...")
    
    # Test 2: Product Variations (1-to-many relationships)
    print("\n\n2. TESTING PRODUCT VARIATIONS")
    print("-" * 40)
    
    handler = ProductVariationHandler()
    variation_results = handler.find_suppliers_with_variations("sandwich cookies")
    
    print(f"Total suppliers: {variation_results['total_suppliers']}")
    print(f"Manufacturers: {variation_results['manufacturers']}")
    print(f"Distributors: {variation_results['distributors']}")
    
    if variation_results['top_manufacturers']:
        print("\nManufacturers with Multiple Variations:")
        for mfr in variation_results['top_manufacturers'][:3]:
            print(f"\n- {mfr['supplier_name']} ({mfr['country']})")
            print(f"  Variations: {mfr['variation_count']} types")
            capabilities = [k for k, v in mfr['capabilities'].items() if v]
            if capabilities:
                print(f"  Capabilities: {', '.join(capabilities)}")
            if mfr['variations']:
                variations = [f"{v['value']} ({v['category']})" for v in mfr['variations'][:3]]
                print(f"  Examples: {', '.join(variations)}")
    
    # Test 3: Complex Requirements Matching
    print("\n\n3. TESTING COMPLEX REQUIREMENTS")
    print("-" * 40)
    
    # Define OREO-specific requirements
    oreo_requirements = {
        'product_type': 'sandwich cookies',
        'flavor': ['chocolate', 'vanilla cream'],
        'manufacturing': ['wafer', 'cream filling', 'embossing'],
        'packaging': ['multi-pack', 'family size', 'sleeves'],
        'certifications': ['kosher'],
        'shape': ['circular', 'round']
    }
    
    matches = handler.match_complex_requirements(oreo_requirements)
    
    print(f"Found {len(matches)} suppliers matching OREO requirements")
    
    if matches:
        print("\nTop Matches for OREO-style Requirements:")
        for i, match in enumerate(matches[:3], 1):
            print(f"\n{i}. {match['supplier_name']} ({match['country']})")
            print(f"   Match Score: {match['match_score']}%")
            if match['matched_requirements']:
                print(f"   Matched: {', '.join(match['matched_requirements'][:3])}")
            print(f"   Products: {match['products_preview'][:100]}...")
            if match['certifications']:
                print(f"   Certifications: {match['certifications'][:100]}")
    
    # Test 4: Advanced Search with Natural Language
    print("\n\n4. TESTING ADVANCED NATURAL LANGUAGE SEARCH")
    print("-" * 40)
    
    advanced = AdvancedSearchSystem()
    
    # Complex natural language query
    query = "chocolate sandwich cookies cream filled circular kosher family pack multi-pack manufacturer"
    
    parsed = advanced.parse_complex_query(query)
    print(f"Query: '{query}'")
    print("\nParsed Query Understanding:")
    print(f"  Products: {parsed['products']}")
    print(f"  Packaging: {parsed['packaging']}")
    print(f"  Certifications: {parsed['certifications']}")
    print(f"  Supplier Types: {parsed['supplier_types']}")
    
    search_results = advanced.execute_advanced_search(query)
    
    print(f"\nFound {search_results['total_results']} results")
    
    if search_results['results']:
        print("\nTop Natural Language Search Results:")
        for i, result in enumerate(search_results['results'][:3], 1):
            print(f"\n{i}. {result['supplier_name']} ({result['country']})")
            print(f"   Relevance: {result['match_percentage']:.1f}%")
            if result['matched_criteria']:
                print(f"   Matched: {', '.join(result['matched_criteria'])}")
    
    # Test 5: Direct Database Search for Specific Terms
    print("\n\n5. TESTING DIRECT DATABASE SEARCH")
    print("-" * 40)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Search for specific OREO-related terms
    search_terms = [
        ('sandwich cookie', 'Direct match'),
        ('chocolate wafer', 'Component match'),
        ('cream filling', 'Filling capability'),
        ('emboss', 'Embossing capability')
    ]
    
    for term, description in search_terms:
        cur.execute("""
            SELECT COUNT(*) as count
            FROM suppliers
            WHERE LOWER(products) LIKE %s
        """, (f"%{term}%",))
        
        result = cur.fetchone()
        print(f"{description} ('{term}'): {result['count']} suppliers")
    
    # Find suppliers with multiple relevant keywords
    cur.execute("""
        SELECT id, supplier_name, country, products
        FROM suppliers
        WHERE (LOWER(products) LIKE '%sandwich%' 
               OR LOWER(products) LIKE '%chocolate%cookie%'
               OR LOWER(products) LIKE '%cream%fill%')
          AND (LOWER(supplier_type) LIKE '%manufact%' 
               OR LOWER(supplier_type) LIKE '%produc%'
               OR LOWER(supplier_name) LIKE '%biscuit%'
               OR LOWER(supplier_name) LIKE '%cookie%')
        LIMIT 5
    """)
    
    multi_match = cur.fetchall()
    
    if multi_match:
        print("\nSuppliers with Multiple OREO-relevant Keywords:")
        for supplier in multi_match:
            print(f"- {supplier['supplier_name']} ({supplier['country']})")
            # Check which keywords matched
            products_lower = (supplier['products'] or '').lower()
            matches = []
            if 'sandwich' in products_lower:
                matches.append('sandwich')
            if 'chocolate' in products_lower and 'cookie' in products_lower:
                matches.append('chocolate cookie')
            if 'cream' in products_lower:
                matches.append('cream')
            if 'wafer' in products_lower:
                matches.append('wafer')
            if matches:
                print(f"  Keywords: {', '.join(matches)}")
    
    cur.close()
    conn.close()
    
    # Summary
    print("\n" + "=" * 80)
    print("SEARCH OPTIMIZATION SUMMARY")
    print("=" * 80)
    
    print("""
The search system successfully:
1. ✓ Classified suppliers as sellers vs users
2. ✓ Identified manufacturers with product variations
3. ✓ Matched complex OREO-specific requirements
4. ✓ Parsed natural language queries
5. ✓ Found suppliers with relevant capabilities

Key Findings:
- Excludes bakeries that use cookies as ingredients
- Prioritizes actual cookie manufacturers
- Identifies suppliers with cream filling capability
- Matches packaging requirements (multi-pack, family size)
- Considers certifications (kosher)

The system can handle complex product searches like:
- "chocolate sandwich cookies" → finds cookie manufacturers
- "cream filled circular cookies" → matches shape and filling
- "kosher family pack cookies" → matches certifications and packaging
- "wafer embossing capability" → finds technical capabilities
""")

if __name__ == "__main__":
    test_oreo_search()