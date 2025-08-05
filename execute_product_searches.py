"""
Execute Product Searches for 4 Categories
========================================
1. Chocolate Sandwich Cookies (OREO-style)
2. Cheese Puffed Ring Snacks (56g)
3. Peanut Puffed Corn Snacks (25g Kids)
4. Wafer Biscuit Product Line (5 SKUs)
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

class ProductSearcher:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        
    def get_db_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def search_suppliers(self, search_terms: list, countries: list, product_name: str, 
                        min_suppliers: int = 50) -> list:
        """Search for suppliers matching product requirements"""
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Build search query
        term_conditions = []
        for term in search_terms:
            term_conditions.append(f"LOWER(products) LIKE '%{term.lower()}%'")
        
        search_condition = " OR ".join(term_conditions)
        
        query = f"""
            SELECT 
                id,
                supplier_name,
                company_name,
                country,
                products,
                company_email,
                company_website,
                contact_person,
                phone,
                verified,
                rating,
                (
                    {" + ".join([f"CASE WHEN LOWER(products) LIKE '%{term.lower()}%' THEN 10 ELSE 0 END" for term in search_terms])}
                    + CASE WHEN country IN %s THEN 20 ELSE 0 END
                    + CASE WHEN verified = true THEN 15 ELSE 0 END
                    + CASE WHEN rating >= 4 THEN 10 ELSE 0 END
                    + CASE WHEN company_email IS NOT NULL AND company_email != '' THEN 20 ELSE 0 END
                    + CASE WHEN LOWER(products) LIKE '%kosher%' OR LOWER(products) LIKE '%halal%' THEN 10 ELSE 0 END
                ) as relevance_score
            FROM suppliers
            WHERE 
                ({search_condition})
                AND products IS NOT NULL 
                AND LENGTH(products) > 200
                AND company_email IS NOT NULL 
                AND company_email != ''
                AND company_email NOT LIKE '%nan%'
            ORDER BY relevance_score DESC, rating DESC NULLS LAST
            LIMIT {min_suppliers * 2}
        """
        
        cur.execute(query, (tuple(countries),))
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        print(f"\n🔍 Search for '{product_name}':")
        print(f"   Found {len(results)} suppliers")
        print(f"   Top countries: {', '.join(set([r['country'] for r in results[:20]])[:5])}")
        
        return results[:min_suppliers]
    
    def save_search_results(self, product_name: str, search_id: str, results: list):
        """Save search results to file for review"""
        
        output = {
            'product': product_name,
            'search_id': search_id,
            'timestamp': datetime.now().isoformat(),
            'total_results': len(results),
            'suppliers': []
        }
        
        for supplier in results:
            output['suppliers'].append({
                'id': supplier['id'],
                'name': supplier['supplier_name'],
                'country': supplier['country'],
                'email': supplier['company_email'],
                'verified': supplier['verified'],
                'rating': float(supplier['rating']) if supplier['rating'] else None,
                'score': supplier['relevance_score'],
                'products_preview': supplier['products'][:200] + '...' if len(supplier['products']) > 200 else supplier['products']
            })
        
        filename = f"search_results_{search_id}_{product_name.replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"   Saved to: {filename}")
        
        return filename


# Execute searches
if __name__ == "__main__":
    searcher = ProductSearcher()
    
    print("🚀 Starting Multi-Product Supplier Search\n")
    
    # Define search parameters for each product
    searches = [
        {
            'id': 'cookies_001',
            'name': 'Chocolate Sandwich Cookies',
            'terms': ['chocolate sandwich cookies', 'sandwich biscuits', 'cream filled cookies', 
                     'chocolate wafer', 'oreo style', 'chocolate biscuit cream'],
            'countries': ['USA', 'Turkey', 'Poland', 'Italy', 'Spain', 'India', 'United Kingdom', 
                         'Germany', 'Netherlands', 'Belgium']
        },
        {
            'id': 'cheese_rings_002',
            'name': 'Cheese Puff Rings',
            'terms': ['cheese puff', 'cheese rings', 'corn puffs', 'extruded snacks', 
                     'cheese snacks', 'puffed corn', 'ring snacks'],
            'countries': ['Netherlands', 'USA', 'Poland', 'Turkey', 'Israel', 'Italy', 
                         'Spain', 'United Kingdom', 'Germany']
        },
        {
            'id': 'peanut_puffs_003',
            'name': 'Peanut Corn Puffs Kids',
            'terms': ['peanut puff', 'corn snacks', 'kids snacks', 'puffed corn', 
                     'natural snacks', 'children snacks', 'peanut flavor'],
            'countries': ['Israel', 'Turkey', 'India', 'Thailand', 'China', 'USA', 
                         'Poland', 'Italy', 'Spain']
        },
        {
            'id': 'wafers_004',
            'name': 'Wafer Biscuits Multi-SKU',
            'terms': ['wafer biscuits', 'wafer cookies', 'cream wafers', 'chocolate wafer', 
                     'layered wafers', 'wafer chocolate', 'strawberry wafer', 'wafer cream'],
            'countries': ['Italy', 'Poland', 'Turkey', 'Greece', 'Germany', 'Spain', 
                         'Belgium', 'Netherlands', 'Austria', 'Switzerland']
        }
    ]
    
    all_results = {}
    
    # Execute each search
    for search in searches:
        results = searcher.search_suppliers(
            search_terms=search['terms'],
            countries=search['countries'],
            product_name=search['name'],
            min_suppliers=50
        )
        
        # Save results
        filename = searcher.save_search_results(
            product_name=search['name'],
            search_id=search['id'],
            results=results
        )
        
        all_results[search['id']] = {
            'product': search['name'],
            'count': len(results),
            'file': filename,
            'top_suppliers': [
                {
                    'name': r['supplier_name'],
                    'country': r['country'],
                    'score': r['relevance_score']
                } for r in results[:5]
            ]
        }
    
    # Summary report
    print("\n📊 SEARCH SUMMARY REPORT")
    print("=" * 60)
    
    total_suppliers = sum([r['count'] for r in all_results.values()])
    print(f"\nTotal unique suppliers found: {total_suppliers}")
    
    for search_id, data in all_results.items():
        print(f"\n{data['product']}:")
        print(f"  - Suppliers found: {data['count']}")
        print(f"  - Results file: {data['file']}")
        print(f"  - Top 3 matches:")
        for i, supplier in enumerate(data['top_suppliers'][:3], 1):
            print(f"    {i}. {supplier['name']} ({supplier['country']}) - Score: {supplier['score']}")
    
    print("\n✅ Search complete! Review the JSON files for detailed supplier information.")
    print("\n📧 Next steps:")
    print("1. Review and filter suppliers in each JSON file")
    print("2. Create targeted email campaigns for each product")
    print("3. Set up tracking and response monitoring")
    
    # Create combined results file
    with open('all_search_results_summary.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n📁 Combined summary saved to: all_search_results_summary.json")