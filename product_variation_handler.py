#!/usr/bin/env python3
"""
Product Variation Handler for FDX.trading
Handles 1-to-many product relationships like:
- Wafer biscuits with multiple flavors/formats
- Puffed snacks with different shapes/seasonings
- Oil products in various packaging sizes
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class ProductVariationHandler:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        
        # Product variation patterns
        self.variation_indicators = {
            'flavors': ['strawberry', 'chocolate', 'vanilla', 'cheese', 'bbq', 'sour cream'],
            'sizes': ['56g', '100g', '220g', '500g', '1kg', '1L', '5L', 'family pack'],
            'formats': ['individual', 'multi-pack', 'bulk', 'retail', 'food service'],
            'coatings': ['chocolate covered', 'yogurt coated', 'sugar coated', 'plain'],
            'packaging': ['bottle', 'pouch', 'box', 'tin', 'bag', 'jar', 'flow wrap']
        }
        
    def identify_product_family(self, product_description: str) -> Dict:
        """
        Identify the core product and its variations
        Example: "Wafer biscuits" -> core product
        Variations: strawberry, chocolate, family pack, etc.
        """
        
        product_lower = product_description.lower()
        
        # Extract core product (remove variation descriptors)
        core_product = product_lower
        variations_found = []
        
        for category, terms in self.variation_indicators.items():
            for term in terms:
                if term in product_lower:
                    variations_found.append({
                        'category': category,
                        'value': term
                    })
                    # Remove variation from core product name
                    core_product = core_product.replace(term, '').strip()
        
        return {
            'core_product': core_product,
            'variations': variations_found,
            'full_description': product_description
        }
    
    def find_suppliers_with_variations(self, product_query: str) -> Dict:
        """
        Find suppliers who offer multiple variations of a product
        """
        
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Search for the core product
        search_term = f"%{product_query.lower()}%"
        
        cur.execute("""
            SELECT 
                id, supplier_name, company_name, country,
                products, company_email, company_website,
                supplier_type, verified, rating
            FROM suppliers
            WHERE LOWER(products) LIKE %s
            OR LOWER(supplier_name) LIKE %s
            LIMIT 200
        """, (search_term, search_term))
        
        suppliers = cur.fetchall()
        
        # Analyze each supplier's product range
        enhanced_suppliers = []
        
        for supplier in suppliers:
            products_text = supplier.get('products', '')
            if not products_text:
                continue
            
            # Parse product variations
            product_family = self.identify_product_family(products_text)
            
            # Count variation types
            variation_count = len(product_family['variations'])
            
            # Check for manufacturing capabilities
            has_manufacturing = any(term in products_text.lower() 
                                  for term in ['manufacturer', 'producer', 'factory', 'production'])
            
            # Check for specific capabilities matching the examples
            capabilities = {
                'extrusion': 'extrud' in products_text.lower(),
                'coating': 'coat' in products_text.lower() or 'enrob' in products_text.lower(),
                'multi_layer': 'layer' in products_text.lower() or 'wafer' in products_text.lower(),
                'seasoning': 'season' in products_text.lower() or 'flavor' in products_text.lower(),
                'packaging_variety': any(pkg in products_text.lower() 
                                       for pkg in ['pouch', 'box', 'bottle', 'bulk'])
            }
            
            enhanced_suppliers.append({
                'supplier_id': supplier['id'],
                'supplier_name': supplier['supplier_name'],
                'company_name': supplier['company_name'] or supplier['supplier_name'],
                'country': supplier['country'] or 'Unknown',
                'email': supplier['company_email'] or '',
                'website': supplier['company_website'] or '',
                'core_product': product_family['core_product'],
                'variation_count': variation_count,
                'variations': product_family['variations'],
                'is_manufacturer': has_manufacturing,
                'capabilities': capabilities,
                'products_preview': products_text[:500],
                'verified': supplier.get('verified', False),
                'rating': float(supplier['rating']) if supplier.get('rating') else None,
                'variation_score': variation_count * 10 + (50 if has_manufacturing else 0)
            })
        
        # Sort by variation score (suppliers with more variations rank higher)
        enhanced_suppliers.sort(key=lambda x: x['variation_score'], reverse=True)
        
        # Group by manufacturing capability
        manufacturers = [s for s in enhanced_suppliers if s['is_manufacturer']]
        distributors = [s for s in enhanced_suppliers if not s['is_manufacturer']]
        
        cur.close()
        conn.close()
        
        return {
            'query': product_query,
            'total_suppliers': len(enhanced_suppliers),
            'manufacturers': len(manufacturers),
            'distributors': len(distributors),
            'top_manufacturers': manufacturers[:20],
            'top_distributors': distributors[:10],
            'all_results': enhanced_suppliers
        }
    
    def match_complex_requirements(self, requirements: Dict) -> List[Dict]:
        """
        Match complex product requirements like the puffed snacks example
        Requirements include shape, flavor, packaging, certifications, etc.
        """
        
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build complex query based on requirements
        conditions = []
        params = []
        
        # Product type
        if requirements.get('product_type'):
            conditions.append("LOWER(products) LIKE %s")
            params.append(f"%{requirements['product_type'].lower()}%")
        
        # Manufacturing process
        if requirements.get('manufacturing'):
            for process in requirements['manufacturing']:
                conditions.append("LOWER(products) LIKE %s")
                params.append(f"%{process.lower()}%")
        
        # Certifications
        if requirements.get('certifications'):
            for cert in requirements['certifications']:
                conditions.append("(LOWER(products) LIKE %s OR LOWER(certifications) LIKE %s)")
                params.extend([f"%{cert.lower()}%", f"%{cert.lower()}%"])
        
        # Country preferences
        if requirements.get('countries'):
            country_conditions = " OR ".join(["country = %s"] * len(requirements['countries']))
            conditions.append(f"({country_conditions})")
            params.extend(requirements['countries'])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT 
                id, supplier_name, company_name, country,
                products, company_email, company_website,
                supplier_type, certifications, verified, rating
            FROM suppliers
            WHERE {where_clause}
            ORDER BY rating DESC NULLS LAST
            LIMIT 100
        """
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        # Score each supplier based on requirement matches
        scored_results = []
        for supplier in results:
            score = 0
            matches = []
            
            products_lower = (supplier.get('products') or '').lower()
            certs_lower = (supplier.get('certifications') or '').lower()
            
            # Check each requirement category
            if requirements.get('product_type') and requirements['product_type'].lower() in products_lower:
                score += 30
                matches.append(f"Product: {requirements['product_type']}")
            
            if requirements.get('shape'):
                for shape in requirements['shape']:
                    if shape.lower() in products_lower:
                        score += 20
                        matches.append(f"Shape: {shape}")
            
            if requirements.get('flavor'):
                for flavor in requirements['flavor']:
                    if flavor.lower() in products_lower:
                        score += 15
                        matches.append(f"Flavor: {flavor}")
            
            if requirements.get('certifications'):
                for cert in requirements['certifications']:
                    if cert.lower() in certs_lower or cert.lower() in products_lower:
                        score += 25
                        matches.append(f"Certification: {cert}")
            
            if requirements.get('packaging'):
                for pkg in requirements['packaging']:
                    if pkg.lower() in products_lower:
                        score += 10
                        matches.append(f"Packaging: {pkg}")
            
            scored_results.append({
                'supplier_id': supplier['id'],
                'supplier_name': supplier['supplier_name'],
                'company_name': supplier['company_name'] or supplier['supplier_name'],
                'country': supplier['country'] or 'Unknown',
                'email': supplier['company_email'] or '',
                'website': supplier['company_website'] or '',
                'products_preview': (supplier['products'] or '')[:500],
                'certifications': supplier['certifications'] or '',
                'verified': supplier.get('verified', False),
                'rating': float(supplier['rating']) if supplier.get('rating') else None,
                'match_score': score,
                'matched_requirements': matches,
                'match_percentage': min(100, score)
            })
        
        # Sort by match score
        scored_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        cur.close()
        conn.close()
        
        return scored_results

def create_variation_search_endpoint(app):
    """Add variation-aware search endpoint to FastAPI"""
    
    @app.post("/api/variation-search")
    async def variation_search(request):
        from fastapi.responses import JSONResponse
        
        data = await request.json()
        query = data.get('query', '')
        
        handler = ProductVariationHandler()
        results = handler.find_suppliers_with_variations(query)
        
        return JSONResponse(
            content=results,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    @app.post("/api/complex-match")
    async def complex_match(request):
        from fastapi.responses import JSONResponse
        
        data = await request.json()
        requirements = data.get('requirements', {})
        
        handler = ProductVariationHandler()
        results = handler.match_complex_requirements(requirements)
        
        return JSONResponse(
            content={'results': results, 'total': len(results)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

if __name__ == "__main__":
    handler = ProductVariationHandler()
    
    # Test with wafer biscuits (your first example)
    print("Testing with 'wafer biscuits' (1-to-many example):")
    print("-" * 60)
    results = handler.find_suppliers_with_variations("wafer biscuits")
    
    print(f"Found {results['total_suppliers']} suppliers")
    print(f"Manufacturers: {results['manufacturers']}")
    print(f"Distributors: {results['distributors']}")
    
    if results['top_manufacturers']:
        print("\nTop manufacturer with variations:")
        top = results['top_manufacturers'][0]
        print(f"  {top['supplier_name']} ({top['country']})")
        print(f"  Variations: {top['variation_count']}")
        print(f"  Capabilities: {[k for k, v in top['capabilities'].items() if v]}")
    
    # Test with puffed snacks (your second example)
    print("\n\nTesting with complex puffed snacks requirements:")
    print("-" * 60)
    
    puffed_requirements = {
        'product_type': 'puffed snacks',
        'shape': ['ring', 'tube', 'cylindrical'],
        'flavor': ['cheese'],
        'manufacturing': ['extrusion', 'extruded'],
        'certifications': ['kosher', 'halal'],
        'packaging': ['pouch', '56g']
    }
    
    matches = handler.match_complex_requirements(puffed_requirements)
    
    print(f"Found {len(matches)} matching suppliers")
    
    if matches:
        print("\nTop match:")
        top = matches[0]
        print(f"  {top['supplier_name']} ({top['country']})")
        print(f"  Match score: {top['match_score']}%")
        print(f"  Matched: {', '.join(top['matched_requirements'][:3])}")