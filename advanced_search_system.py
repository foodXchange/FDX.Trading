#!/usr/bin/env python3
"""
Advanced Search System for FDX.trading
Supports complex multi-criteria searches with AI-powered matching
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re
from typing import List, Dict, Optional
from datetime import datetime
import json

class AdvancedSearchSystem:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        
    def parse_complex_query(self, query: str) -> Dict:
        """
        Parse complex queries like:
        - "sunflower oil 1L plastic bottle Italy Spain"
        - "organic olive oil glass bottle 500ml-750ml certified"
        - "pasta gluten-free Italy OR Greece under $5"
        """
        parsed = {
            'products': [],
            'packaging': [],
            'sizes': [],
            'countries': [],
            'certifications': [],
            'price_range': None,
            'exclude_terms': [],
            'must_have_all': [],
            'supplier_types': []
        }
        
        # Common packaging terms
        packaging_terms = ['bottle', 'bottles', 'can', 'cans', 'jar', 'jars', 'bag', 'bags', 
                          'box', 'boxes', 'plastic', 'glass', 'metal', 'carton', 'pouch', 'tin']
        
        # Size patterns (e.g., 1L, 500ml, 1kg, etc.)
        size_pattern = r'\b(\d+(?:\.\d+)?)\s*(L|l|ml|ML|kg|KG|g|G|oz|OZ|lb|LB)\b'
        
        # Country list (expand as needed)
        countries = ['Italy', 'Spain', 'Greece', 'Turkey', 'India', 'China', 'USA', 
                    'Germany', 'France', 'Netherlands', 'Belgium', 'Portugal', 'Brazil',
                    'Argentina', 'Mexico', 'Thailand', 'Vietnam', 'Indonesia']
        
        # Certification keywords
        cert_keywords = ['organic', 'certified', 'ISO', 'HACCP', 'BRC', 'halal', 'kosher',
                        'fair trade', 'fairtrade', 'non-gmo', 'gluten-free', 'vegan']
        
        # Supplier type keywords
        supplier_keywords = ['manufacturer', 'producer', 'distributor', 'exporter', 
                           'importer', 'wholesaler', 'factory', 'farm']
        
        # Process query
        query_lower = query.lower()
        query_words = query.split()
        
        # Extract sizes
        sizes = re.findall(size_pattern, query, re.IGNORECASE)
        for size in sizes:
            parsed['sizes'].append(f"{size[0]}{size[1]}")
            # Remove size from query for further processing
            query_lower = query_lower.replace(f"{size[0]}{size[1]}".lower(), "")
        
        # Extract countries
        for country in countries:
            if country.lower() in query_lower:
                parsed['countries'].append(country)
                query_lower = query_lower.replace(country.lower(), "")
        
        # Extract packaging
        for term in packaging_terms:
            if term in query_lower:
                parsed['packaging'].append(term)
                query_lower = query_lower.replace(term, "")
        
        # Extract certifications
        for cert in cert_keywords:
            if cert in query_lower:
                parsed['certifications'].append(cert)
                query_lower = query_lower.replace(cert, "")
        
        # Extract supplier types
        for stype in supplier_keywords:
            if stype in query_lower:
                parsed['supplier_types'].append(stype)
                query_lower = query_lower.replace(stype, "")
        
        # Extract exclusions (words after NOT or -)
        exclusion_pattern = r'(?:NOT|-)\s*(\w+)'
        exclusions = re.findall(exclusion_pattern, query, re.IGNORECASE)
        parsed['exclude_terms'] = exclusions
        
        # Extract must-have terms (in quotes or with +)
        must_have_pattern = r'["\']([^"\']+)["\']|\+(\w+)'
        must_haves = re.findall(must_have_pattern, query, re.IGNORECASE)
        for match in must_haves:
            term = match[0] if match[0] else match[1]
            if term:
                parsed['must_have_all'].append(term)
        
        # Remaining words are product terms
        remaining_words = query_lower.split()
        for word in remaining_words:
            # Skip small words and already processed terms
            if len(word) > 2 and word not in ['and', 'or', 'the', 'for', 'with']:
                if not any(word in term for term in parsed['exclude_terms']):
                    parsed['products'].append(word)
        
        return parsed
    
    def build_advanced_query(self, parsed_query: Dict) -> tuple:
        """Build SQL query from parsed complex query"""
        
        conditions = []
        params = []
        scoring_parts = []
        
        # Product search (most important)
        if parsed_query['products']:
            product_conditions = []
            for product in parsed_query['products']:
                product_conditions.append("(LOWER(products) LIKE %s OR LOWER(supplier_name) LIKE %s)")
                params.extend([f"%{product}%", f"%{product}%"])
                # Add to scoring
                scoring_parts.append(f"CASE WHEN LOWER(products) LIKE %s THEN 10 ELSE 0 END")
                params.append(f"%{product}%")
            
            if product_conditions:
                conditions.append(f"({' OR '.join(product_conditions)})")
        
        # Must have all terms
        if parsed_query['must_have_all']:
            for term in parsed_query['must_have_all']:
                conditions.append("(LOWER(products) LIKE %s)")
                params.append(f"%{term}%")
                scoring_parts.append("20")  # High score for must-have terms
        
        # Packaging filter
        if parsed_query['packaging']:
            packaging_conditions = []
            for pack in parsed_query['packaging']:
                packaging_conditions.append("LOWER(products) LIKE %s")
                params.append(f"%{pack}%")
                scoring_parts.append(f"CASE WHEN LOWER(products) LIKE %s THEN 5 ELSE 0 END")
                params.append(f"%{pack}%")
            
            if packaging_conditions:
                conditions.append(f"({' OR '.join(packaging_conditions)})")
        
        # Size filter
        if parsed_query['sizes']:
            size_conditions = []
            for size in parsed_query['sizes']:
                # Handle different size formats
                size_conditions.append("LOWER(products) LIKE %s")
                params.append(f"%{size}%")
                scoring_parts.append(f"CASE WHEN LOWER(products) LIKE %s THEN 8 ELSE 0 END")
                params.append(f"%{size}%")
            
            if size_conditions:
                conditions.append(f"({' OR '.join(size_conditions)})")
        
        # Country filter
        if parsed_query['countries']:
            country_conditions = []
            for country in parsed_query['countries']:
                country_conditions.append("country = %s")
                params.append(country)
                scoring_parts.append(f"CASE WHEN country = %s THEN 15 ELSE 0 END")
                params.append(country)
            
            if country_conditions:
                conditions.append(f"({' OR '.join(country_conditions)})")
        
        # Certifications
        if parsed_query['certifications']:
            cert_conditions = []
            for cert in parsed_query['certifications']:
                cert_conditions.append("LOWER(products) LIKE %s")
                params.append(f"%{cert}%")
                scoring_parts.append(f"CASE WHEN LOWER(products) LIKE %s THEN 7 ELSE 0 END")
                params.append(f"%{cert}%")
            
            if cert_conditions:
                conditions.append(f"({' OR '.join(cert_conditions)})")
        
        # Supplier types
        if parsed_query['supplier_types']:
            type_conditions = []
            for stype in parsed_query['supplier_types']:
                type_conditions.append("LOWER(supplier_type) LIKE %s")
                params.append(f"%{stype}%")
                scoring_parts.append(f"CASE WHEN LOWER(supplier_type) LIKE %s THEN 5 ELSE 0 END")
                params.append(f"%{stype}%")
            
            if type_conditions:
                conditions.append(f"({' OR '.join(type_conditions)})")
        
        # Exclusions
        if parsed_query['exclude_terms']:
            for term in parsed_query['exclude_terms']:
                conditions.append("(LOWER(products) NOT LIKE %s AND LOWER(supplier_name) NOT LIKE %s)")
                params.extend([f"%{term}%", f"%{term}%"])
        
        # Build final query
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Calculate relevance score
        if scoring_parts:
            score_calculation = " + ".join(scoring_parts)
        else:
            score_calculation = "1"
        
        query = f"""
            SELECT 
                id as supplier_id,
                supplier_name,
                company_name,
                country,
                products,
                company_email as email,
                company_website as website,
                supplier_type,
                verified,
                rating,
                ({score_calculation}) as relevance_score
            FROM suppliers
            WHERE {where_clause}
            ORDER BY relevance_score DESC, rating DESC NULLS LAST
            LIMIT 100
        """
        
        return query, params
    
    def execute_advanced_search(self, query_string: str, filters: Optional[Dict] = None) -> Dict:
        """Execute advanced search with complex query parsing"""
        
        start_time = datetime.now()
        
        # Parse the complex query
        parsed = self.parse_complex_query(query_string)
        
        # Apply additional filters if provided
        if filters:
            if filters.get('countries'):
                parsed['countries'].extend(filters['countries'])
            if filters.get('verified_only'):
                # Will add to query
                pass
            if filters.get('min_rating'):
                # Will add to query
                pass
        
        # Build SQL query
        sql_query, params = self.build_advanced_query(parsed)
        
        # Execute query
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(sql_query, params)
            results = cursor.fetchall()
            
            # Format results
            formatted_results = []
            for idx, row in enumerate(results, 1):
                # Calculate match percentage based on relevance score
                relevance = row.get('relevance_score', 0)
                max_possible_score = 100  # Adjust based on your scoring
                match_percentage = min(100, (relevance / max_possible_score) * 100)
                
                formatted_results.append({
                    'rank': idx,
                    'supplier_id': row['supplier_id'],
                    'supplier_name': row['supplier_name'],
                    'company_name': row['company_name'] or row['supplier_name'],
                    'country': row['country'] or 'Unknown',
                    'email': row['email'] or '',
                    'website': row['website'] or '',
                    'supplier_type': row['supplier_type'] or '',
                    'verified': row.get('verified', False),
                    'rating': float(row['rating']) if row.get('rating') else None,
                    'product_preview': row['products'][:500] if row.get('products') else '',
                    'relevance_score': relevance,
                    'match_percentage': match_percentage,
                    'matched_criteria': self._get_matched_criteria(row, parsed)
                })
            
            cursor.close()
            conn.close()
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'query': query_string,
                'parsed_query': parsed,
                'total_results': len(formatted_results),
                'execution_time_ms': int(execution_time),
                'timestamp': datetime.now().isoformat(),
                'results': formatted_results
            }
            
        except Exception as e:
            print(f"Search error: {e}")
            return {
                'query': query_string,
                'error': str(e),
                'total_results': 0,
                'results': []
            }
    
    def _get_matched_criteria(self, row: Dict, parsed: Dict) -> List[str]:
        """Identify which criteria matched for this supplier"""
        matched = []
        
        products_lower = (row.get('products') or '').lower()
        
        for product in parsed['products']:
            if product in products_lower:
                matched.append(f"Product: {product}")
        
        for pack in parsed['packaging']:
            if pack in products_lower:
                matched.append(f"Packaging: {pack}")
        
        for size in parsed['sizes']:
            if size.lower() in products_lower:
                matched.append(f"Size: {size}")
        
        if row.get('country') in parsed['countries']:
            matched.append(f"Country: {row['country']}")
        
        return matched[:5]  # Return top 5 matches

# FastAPI endpoint integration
def create_advanced_search_endpoint(app):
    """Add advanced search endpoint to FastAPI app"""
    
    @app.post("/api/advanced-search")
    async def advanced_search(request):
        from fastapi.responses import JSONResponse
        
        data = await request.json()
        query = data.get('query', '')
        filters = data.get('filters', {})
        
        search_system = AdvancedSearchSystem()
        results = search_system.execute_advanced_search(query, filters)
        
        return JSONResponse(
            content=results,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    return app

if __name__ == "__main__":
    # Test the advanced search
    from dotenv import load_dotenv
    load_dotenv()
    
    search = AdvancedSearchSystem()
    
    # Test complex queries
    test_queries = [
        "sunflower oil 1L plastic bottle Italy Spain",
        "organic olive oil glass bottle 500ml certified",
        "pasta gluten-free manufacturer Italy -wheat",
        '"extra virgin" olive oil Italy 750ml bottle'
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        parsed = search.parse_complex_query(query)
        print(f"Parsed: {json.dumps(parsed, indent=2)}")
        
        results = search.execute_advanced_search(query)
        print(f"Found {results['total_results']} results")
        
        if results['results']:
            top_result = results['results'][0]
            print(f"Top match: {top_result['supplier_name']} ({top_result['country']})")
            print(f"Match: {top_result['match_percentage']:.1f}%")
            print(f"Matched criteria: {', '.join(top_result['matched_criteria'])}")