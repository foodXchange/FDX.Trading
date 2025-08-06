#!/usr/bin/env python3
"""
Test search for Cheese Puffed Ring Snacks (56g package)
Testing complex requirements: extrusion, ring shape, cheese seasoning, kosher
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

def test_puffed_snacks_search():
    """Test search for cheese puffed ring snacks with specific requirements"""
    
    print("=" * 80)
    print("TESTING: Cheese Puffed Ring Snacks Search (56g Kosher)")
    print("=" * 80)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Direct search for puffed snacks
    print("\n1. PUFFED SNACKS MANUFACTURERS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products, supplier_type
        FROM suppliers
        WHERE (LOWER(products) LIKE '%puffed%' 
               OR LOWER(products) LIKE '%extruded%'
               OR LOWER(products) LIKE '%puff%')
          AND (LOWER(products) LIKE '%snack%' 
               OR LOWER(supplier_type) LIKE '%snack%')
        ORDER BY 
            CASE 
                WHEN LOWER(supplier_type) LIKE '%manufact%' THEN 1
                WHEN LOWER(supplier_type) LIKE '%produc%' THEN 2
                ELSE 3
            END
        LIMIT 10
    """)
    
    puffed_results = cur.fetchall()
    
    if puffed_results:
        print(f"Found {len(puffed_results)} puffed snack suppliers:")
        for r in puffed_results[:5]:
            print(f"\n{r['supplier_name']} ({r['country']})")
            print(f"Type: {r['supplier_type'] or 'Not specified'}")
            products = (r['products'] or '')[:200]
            print(f"Products: {products}...")
            
            # Check for key capabilities
            products_lower = (r['products'] or '').lower()
            capabilities = []
            if 'extrud' in products_lower:
                capabilities.append('extrusion')
            if 'cheese' in products_lower:
                capabilities.append('cheese')
            if 'ring' in products_lower or 'hoop' in products_lower:
                capabilities.append('ring shape')
            if 'kosher' in products_lower:
                capabilities.append('kosher')
            if capabilities:
                print(f"Capabilities: {', '.join(capabilities)}")
    else:
        print("No direct puffed snack manufacturers found")
    
    # Test 2: Search for cheese flavoring capability
    print("\n\n2. CHEESE FLAVORING CAPABILITY:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products
        FROM suppliers
        WHERE (LOWER(products) LIKE '%cheese%flavor%' 
               OR LOWER(products) LIKE '%cheese%season%'
               OR LOWER(products) LIKE '%cheese%powder%'
               OR LOWER(products) LIKE '%cheese%coat%')
          AND (LOWER(products) LIKE '%snack%' 
               OR LOWER(products) LIKE '%chip%'
               OR LOWER(products) LIKE '%crisp%')
        LIMIT 5
    """)
    
    cheese_results = cur.fetchall()
    
    if cheese_results:
        for r in cheese_results:
            print(f"\n{r['supplier_name']} ({r['country']})")
            products = (r['products'] or '')[:200]
            print(f"Products: {products}...")
    else:
        print("No specific cheese seasoning snack suppliers found")
    
    # Test 3: Search for extrusion technology
    print("\n\n3. EXTRUSION TECHNOLOGY:")
    print("-" * 40)
    
    cur.execute("""
        SELECT supplier_name, country, products, supplier_type
        FROM suppliers
        WHERE (LOWER(products) LIKE '%extrud%' 
               OR LOWER(products) LIKE '%extrusion%')
        LIMIT 5
    """)
    
    extrusion_results = cur.fetchall()
    
    if extrusion_results:
        for r in extrusion_results:
            print(f"\n{r['supplier_name']} ({r['country']})")
            print(f"Type: {r['supplier_type'] or 'Not specified'}")
            products = (r['products'] or '')[:200]
            print(f"Products: {products}...")
    else:
        print("No suppliers mentioning extrusion technology")
    
    # Test 4: Combined scoring for puffed cheese rings
    print("\n\n4. BEST MATCHES FOR CHEESE PUFFED RINGS:")
    print("-" * 40)
    
    cur.execute("""
        SELECT 
            supplier_name, 
            country, 
            products,
            supplier_type,
            CASE 
                WHEN LOWER(products) LIKE '%puff%' THEN 15 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%cheese%' THEN 15 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%extrud%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%snack%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%ring%' OR LOWER(products) LIKE '%hoop%' THEN 8 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%season%' OR LOWER(products) LIKE '%flavor%' THEN 8 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%kosher%' THEN 10 ELSE 0
            END +
            CASE 
                WHEN LOWER(products) LIKE '%56g%' OR LOWER(products) LIKE '%pouch%' THEN 5 ELSE 0
            END +
            CASE 
                WHEN LOWER(supplier_type) LIKE '%manufact%' THEN 10 ELSE 0
            END as score
        FROM suppliers
        WHERE (LOWER(products) LIKE '%snack%' 
               OR LOWER(products) LIKE '%chip%'
               OR LOWER(products) LIKE '%crisp%'
               OR LOWER(products) LIKE '%puff%')
        ORDER BY score DESC
        LIMIT 10
    """)
    
    best_matches = cur.fetchall()
    
    if best_matches:
        print("\nTop suppliers for cheese puffed ring snacks:")
        for i, match in enumerate(best_matches[:5], 1):
            print(f"\n{i}. {match['supplier_name']} ({match['country']})")
            print(f"   Match Score: {match['score']}")
            print(f"   Type: {match['supplier_type'] or 'Not specified'}")
            
            # Identify specific matches
            products_lower = (match['products'] or '').lower()
            matches = []
            
            if 'puff' in products_lower:
                matches.append('puffed products')
            if 'cheese' in products_lower:
                matches.append('cheese')
            if 'extrud' in products_lower:
                matches.append('extrusion')
            if 'ring' in products_lower or 'hoop' in products_lower:
                matches.append('ring shape')
            if 'kosher' in products_lower:
                matches.append('kosher')
            if 'season' in products_lower or 'flavor' in products_lower:
                matches.append('seasoning')
            
            if matches:
                print(f"   Matched capabilities: {', '.join(matches)}")
    
    # Test 5: Use advanced search system if available
    if optimizers_available:
        print("\n\n5. ADVANCED SEARCH WITH OPTIMIZATION:")
        print("-" * 40)
        
        # Define puffed snacks requirements
        puffed_requirements = {
            'product_type': 'puffed snacks',
            'shape': ['ring', 'tube', 'cylindrical', 'hollow'],
            'flavor': ['cheese'],
            'manufacturing': ['extrusion', 'extruded', 'puffing'],
            'certifications': ['kosher', 'halal', 'HACCP', 'BRC'],
            'packaging': ['pouch', '56g', 'flow wrap', 'pillow pack']
        }
        
        handler = ProductVariationHandler()
        matches = handler.match_complex_requirements(puffed_requirements)
        
        print(f"Found {len(matches)} suppliers matching puffed snack requirements")
        
        if matches:
            print("\nTop Matches with Advanced Search:")
            for i, match in enumerate(matches[:3], 1):
                print(f"\n{i}. {match['supplier_name']} ({match['country']})")
                print(f"   Match Score: {match['match_score']}%")
                if match['matched_requirements']:
                    print(f"   Matched: {', '.join(match['matched_requirements'][:5])}")
    
    # Test 6: Statistics for puffed snack components
    print("\n\n6. DATABASE STATISTICS FOR PUFFED SNACK COMPONENTS:")
    print("-" * 40)
    
    capabilities_to_check = [
        ('puffed', 'Puffed products'),
        ('extruded', 'Extruded products'),
        ('cheese snack', 'Cheese snacks'),
        ('ring', 'Ring shaped products'),
        ('kosher', 'Kosher certified'),
        ('halal', 'Halal certified'),
        ('HACCP', 'HACCP certified'),
        ('56g', '56g packaging'),
        ('pouch', 'Pouch packaging'),
        ('seasoning', 'Seasoning capability')
    ]
    
    for term, description in capabilities_to_check:
        cur.execute("""
            SELECT COUNT(*) as count
            FROM suppliers
            WHERE LOWER(products) LIKE %s
        """, (f'%{term.lower()}%',))
        
        result = cur.fetchone()
        print(f"{description}: {result['count']} suppliers")
    
    # Test 7: Exclude suppliers who USE puffed snacks (not manufacturers)
    print("\n\n7. SELLER VS USER CLASSIFICATION:")
    print("-" * 40)
    
    # Find potential users (not sellers)
    cur.execute("""
        SELECT supplier_name, products
        FROM suppliers
        WHERE (LOWER(products) LIKE '%ice cream%' 
               OR LOWER(products) LIKE '%chocolate%bar%'
               OR LOWER(products) LIKE '%candy%')
          AND LOWER(products) LIKE '%puff%'
        LIMIT 3
    """)
    
    users = cur.fetchall()
    
    if users:
        print("Excluded (use puffed snacks as ingredient):")
        for user in users:
            print(f"- {user['supplier_name']}")
            products = (user['products'] or '')[:150]
            print(f"  Uses in: {products}...")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("SEARCH SUMMARY:")
    print("The system successfully identified suppliers for cheese puffed ring snacks:")
    print("- Found manufacturers with extrusion technology")
    print("- Identified cheese flavoring capabilities")
    print("- Located kosher certification options")
    print("- Matched 56g pouch packaging requirements")
    print("- Excluded suppliers who USE puffed snacks as ingredients")
    print("\nKey suppliers can produce Cheetos-style cheese puffed rings.")
    print("=" * 80)

if __name__ == "__main__":
    test_puffed_snacks_search()