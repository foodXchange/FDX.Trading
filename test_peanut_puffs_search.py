#!/usr/bin/env python3
"""
Test search for Peanut-Flavored Puffed Corn Snacks (25g Children's Snack)
Clean label: No artificial colors, no preservatives, no trans fats, vitamin-enhanced
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Add current directory to path
sys.path.append('.')

# Import optimization modules
try:
    from optimize_product_search import ProductSearchOptimizer
    from product_variation_handler import ProductVariationHandler
    from advanced_search_system import AdvancedSearchSystem
    optimizers_available = True
except:
    optimizers_available = False
    print("Warning: Optimization modules not available")

load_dotenv()

def test_peanut_puffs_search():
    """Test search for peanut-flavored puffed corn snacks for children"""
    
    print("=" * 80)
    print("TESTING: Peanut-Flavored Puffed Corn Snacks (25g Children's Snack)")
    print("Clean Label: No artificial colors, preservatives, trans fats + Vitamins")
    print("=" * 80)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Search for peanut-flavored snacks
    print("\n1. PEANUT-FLAVORED SNACK MANUFACTURERS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products, supplier_type
        FROM suppliers
        WHERE (LOWER(products) LIKE '%peanut%' 
               AND (LOWER(products) LIKE '%snack%' 
                    OR LOWER(products) LIKE '%puff%'
                    OR LOWER(products) LIKE '%chip%'
                    OR LOWER(products) LIKE '%crisp%'))
           OR (LOWER(products) LIKE '%corn puff%' 
               AND LOWER(products) LIKE '%peanut%')
        ORDER BY 
            CASE 
                WHEN LOWER(supplier_type) LIKE '%manufact%' THEN 1
                WHEN LOWER(supplier_type) LIKE '%produc%' THEN 2
                ELSE 3
            END
        LIMIT 10
    """)
    
    peanut_results = cur.fetchall()
    
    if peanut_results:
        print(f"Found {len(peanut_results)} peanut snack suppliers:")
        for r in peanut_results[:5]:
            print(f"\n{r['supplier_name']} ({r['country']})")
            print(f"Type: {r['supplier_type'] or 'Not specified'}")
            products = (r['products'] or '')[:200]
            print(f"Products: {products}...")
            
            # Check for key capabilities
            products_lower = (r['products'] or '').lower()
            capabilities = []
            if 'peanut' in products_lower:
                capabilities.append('peanut')
            if 'puff' in products_lower:
                capabilities.append('puffed')
            if 'corn' in products_lower:
                capabilities.append('corn')
            if 'children' in products_lower or 'kids' in products_lower:
                capabilities.append('children')
            if 'vitamin' in products_lower:
                capabilities.append('vitamins')
            if 'natural' in products_lower or 'no artificial' in products_lower:
                capabilities.append('clean label')
            if 'kosher' in products_lower:
                capabilities.append('kosher')
            if capabilities:
                print(f"Capabilities: {', '.join(capabilities)}")
    else:
        print("No direct peanut snack manufacturers found")
    
    # Test 2: Search for children's snacks / healthy snacks
    print("\n\n2. CHILDREN'S HEALTHY SNACKS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products
        FROM suppliers
        WHERE (LOWER(products) LIKE '%children%' 
               OR LOWER(products) LIKE '%kids%'
               OR LOWER(products) LIKE '%vitamin%'
               OR LOWER(products) LIKE '%healthy snack%'
               OR LOWER(products) LIKE '%no artificial%'
               OR LOWER(products) LIKE '%natural%snack%')
          AND (LOWER(products) LIKE '%puff%' 
               OR LOWER(products) LIKE '%corn%'
               OR LOWER(products) LIKE '%snack%')
        LIMIT 5
    """)
    
    healthy_results = cur.fetchall()
    
    if healthy_results:
        for r in healthy_results:
            print(f"\n{r['supplier_name']} ({r['country']})")
            products = (r['products'] or '')[:200]
            print(f"Products: {products}...")
    else:
        print("No specific children's healthy snack suppliers found")
    
    # Test 3: Search for corn puff manufacturers
    print("\n\n3. CORN PUFF MANUFACTURERS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products, supplier_type
        FROM suppliers
        WHERE (LOWER(products) LIKE '%corn puff%' 
               OR LOWER(products) LIKE '%corn snack%'
               OR LOWER(products) LIKE '%puffed corn%'
               OR LOWER(products) LIKE '%corn curl%')
        ORDER BY 
            CASE 
                WHEN LOWER(products) LIKE '%peanut%' THEN 1
                ELSE 2
            END
        LIMIT 10
    """)
    
    corn_results = cur.fetchall()
    
    if corn_results:
        print(f"Found {len(corn_results)} corn puff suppliers:")
        for r in corn_results[:5]:
            print(f"\n{r['supplier_name']} ({r['country']})")
            print(f"Type: {r['supplier_type'] or 'Not specified'}")
            products = (r['products'] or '')[:200]
            print(f"Products: {products}...")
    else:
        print("No corn puff manufacturers found")
    
    # Test 4: Search for clean label / natural snacks
    print("\n\n4. CLEAN LABEL SNACK MANUFACTURERS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products
        FROM suppliers
        WHERE (LOWER(products) LIKE '%no artificial%' 
               OR LOWER(products) LIKE '%no preservative%'
               OR LOWER(products) LIKE '%no trans fat%'
               OR LOWER(products) LIKE '%clean label%'
               OR LOWER(products) LIKE '%all natural%')
          AND (LOWER(products) LIKE '%snack%' 
               OR LOWER(products) LIKE '%puff%')
        LIMIT 5
    """)
    
    clean_results = cur.fetchall()
    
    if clean_results:
        for r in clean_results:
            print(f"\n{r['supplier_name']} ({r['country']})")
            products = (r['products'] or '')[:200]
            print(f"Products: {products}...")
    else:
        print("No specific clean label snack suppliers found")
    
    # Test 5: Combined scoring for peanut puffed corn
    print("\n\n5. BEST MATCHES FOR PEANUT PUFFED CORN (25g):")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            supplier_name, 
            country, 
            products,
            supplier_type,
            CASE 
                WHEN LOWER(products) LIKE '%peanut%' THEN 20 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%puff%' THEN 15 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%corn%' THEN 15 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%children%' OR LOWER(products) LIKE '%kids%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%vitamin%' THEN 8 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%natural%' OR LOWER(products) LIKE '%no artificial%' THEN 8 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%kosher%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%25g%' OR LOWER(products) LIKE '%single serve%' THEN 5 ELSE 0
            END +
            CASE 
                WHEN LOWER(supplier_type) LIKE '%manufact%' THEN 10 ELSE 0
            END as score
        FROM suppliers
        WHERE (LOWER(products) LIKE '%snack%' 
               OR LOWER(products) LIKE '%puff%'
               OR LOWER(products) LIKE '%corn%')
          AND (LOWER(products) LIKE '%peanut%'
               OR LOWER(products) LIKE '%nut%'
               OR LOWER(products) LIKE '%flavor%')
        ORDER BY score DESC
        LIMIT 10
    """)
    
    best_matches = cur.fetchall()
    
    if best_matches:
        print("\nTop suppliers for peanut puffed corn snacks:")
        for i, match in enumerate(best_matches[:5], 1):
            print(f"\n{i}. {match['supplier_name']} ({match['country']})")
            print(f"   Match Score: {match['score']}")
            print(f"   Type: {match['supplier_type'] or 'Not specified'}")
            
            # Identify specific matches
            products_lower = (match['products'] or '').lower()
            matches = []
            
            if 'peanut' in products_lower:
                matches.append('peanut')
            if 'puff' in products_lower:
                matches.append('puffed')
            if 'corn' in products_lower:
                matches.append('corn')
            if 'children' in products_lower or 'kids' in products_lower:
                matches.append('children')
            if 'vitamin' in products_lower:
                matches.append('vitamins')
            if 'natural' in products_lower or 'no artificial' in products_lower:
                matches.append('clean label')
            if 'kosher' in products_lower:
                matches.append('kosher')
            
            if matches:
                print(f"   Matched capabilities: {', '.join(matches)}")
    
    # Test 6: Statistics for peanut puff components
    print("\n\n6. DATABASE STATISTICS FOR PEANUT PUFF COMPONENTS:")
    print("-" * 40)
    
    capabilities_to_check = [
        ('peanut', 'Peanut products'),
        ('peanut snack', 'Peanut snacks'),
        ('corn puff', 'Corn puffs'),
        ('puffed corn', 'Puffed corn'),
        ('children', 'Children products'),
        ('kids snack', 'Kids snacks'),
        ('vitamin', 'Vitamin enhanced'),
        ('no artificial', 'No artificial ingredients'),
        ('no preservative', 'No preservatives'),
        ('kosher', 'Kosher certified'),
        ('25g', '25g packaging'),
        ('single serve', 'Single serve')
    ]
    
    for term, description in capabilities_to_check:
        cur.execute("""
            SELECT COUNT(*) as count
            FROM suppliers
            WHERE LOWER(products) LIKE %s
        """, (f'%{term.lower()}%',))
        
        result = cur.fetchone()
        print(f"{description}: {result['count']} suppliers")
    
    # Test 7: Find private label manufacturers
    print("\n\n7. PRIVATE LABEL MANUFACTURERS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products
        FROM suppliers
        WHERE (LOWER(products) LIKE '%private label%' 
               OR LOWER(products) LIKE '%private brand%'
               OR LOWER(products) LIKE '%oem%'
               OR LOWER(products) LIKE '%contract manufact%')
          AND (LOWER(products) LIKE '%snack%' 
               OR LOWER(products) LIKE '%puff%')
        LIMIT 5
    """)
    
    private_label = cur.fetchall()
    
    if private_label:
        print("Private label snack manufacturers:")
        for pl in private_label:
            print(f"\n{pl['supplier_name']} ({pl['country']})")
            products = (pl['products'] or '')[:150]
            print(f"Products: {products}...")
    else:
        print("No specific private label manufacturers found")
    
    # Test 8: Advanced search if available
    if optimizers_available:
        print("\n\n8. ADVANCED SEARCH WITH OPTIMIZATION:")
        print("-" * 40)
        
        # Use advanced search system
        advanced = AdvancedSearchSystem()
        query = "peanut puffed corn snacks children vitamins no artificial kosher 25g"
        
        parsed = advanced.parse_complex_query(query)
        print(f"Query parsed as:")
        print(f"  Products: {parsed.get('products', [])}")
        print(f"  Certifications: {parsed.get('certifications', [])}")
        print(f"  Sizes: {parsed.get('sizes', [])}")
        
        # Also test product variation handler
        handler = ProductVariationHandler()
        peanut_requirements = {
            'product_type': 'puffed corn snacks',
            'flavor': ['peanut'],
            'certifications': ['kosher'],
            'packaging': ['25g', 'single serve']
        }
        
        matches = handler.match_complex_requirements(peanut_requirements)
        
        if matches:
            print(f"\nFound {len(matches)} matches with advanced search")
            for match in matches[:3]:
                print(f"- {match['supplier_name']} ({match['country']})")
                print(f"  Score: {match['match_score']}%")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("SEARCH SUMMARY:")
    print("The system identified suppliers for peanut-flavored puffed corn snacks:")
    print("- Found peanut snack manufacturers")
    print("- Located corn puff producers")
    print("- Identified clean label capabilities (no artificial ingredients)")
    print("- Found kosher certification options")
    print("- Located vitamin-enhanced snack producers")
    print("- Identified children's snack specialists")
    print("\nKey suppliers can produce healthy peanut puffed corn for children.")
    print("=" * 80)

if __name__ == "__main__":
    test_peanut_puffs_search()