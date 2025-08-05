# AI-Powered Supplier Search System
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
from typing import List, Dict
import re

load_dotenv()

# Azure OpenAI configuration
client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

class AISupplierSearch:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def analyze_product_request(self, product_description: str) -> Dict:
        """Use AI to analyze the product request and extract key requirements"""
        prompt = f"""
        Analyze this product sourcing request and extract key search criteria:
        
        {product_description}
        
        Return a JSON with:
        {{
            "product_types": ["list of specific product types to search for"],
            "key_requirements": ["list of must-have features"],
            "certifications": ["required certifications"],
            "manufacturing_capabilities": ["required manufacturing processes"],
            "search_keywords": ["keywords for database search"],
            "nice_to_have": ["optional features"]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a food industry sourcing expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        return json.loads(content[content.find('{'):content.rfind('}')+1])
    
    def search_suppliers(self, criteria: Dict) -> List[Dict]:
        """Search database for suppliers matching criteria"""
        # Build search query
        search_conditions = []
        params = []
        
        # Search by keywords
        keyword_conditions = []
        for keyword in criteria.get('search_keywords', []):
            keyword_conditions.append("""
                (LOWER(products) LIKE %s OR 
                 LOWER(supplier_type) LIKE %s OR 
                 LOWER(supplier_name) LIKE %s)
            """)
            kw = f'%{keyword.lower()}%'
            params.extend([kw, kw, kw])
        
        if keyword_conditions:
            search_conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        # Build final query
        where_clause = ' AND '.join(search_conditions) if search_conditions else '1=1'
        
        query = f"""
            SELECT id, supplier_name, company_name, country, products, 
                   supplier_type, company_email, company_website
            FROM suppliers
            WHERE {where_clause}
            AND products IS NOT NULL
            LIMIT 500
        """
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def score_supplier(self, supplier: Dict, criteria: Dict, product_description: str) -> float:
        """Use AI to score how well a supplier matches the requirements"""
        prompt = f"""
        Score this supplier for the following product request (0-100):
        
        PRODUCT REQUEST:
        {product_description}
        
        KEY REQUIREMENTS:
        {json.dumps(criteria, indent=2)}
        
        SUPPLIER INFO:
        Name: {supplier['supplier_name']}
        Country: {supplier['country']}
        Type: {supplier['supplier_type']}
        Products: {supplier['products'][:500]}
        
        Return only a JSON with:
        {{
            "score": 0-100,
            "reasons": ["why this supplier matches or doesn't match"],
            "strengths": ["supplier strengths for this product"],
            "concerns": ["potential issues or gaps"]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a food sourcing expert. Be critical and accurate in scoring."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            result = json.loads(content[content.find('{'):content.rfind('}')+1])
            return result
        except:
            return {"score": 0, "reasons": ["Error analyzing supplier"], "strengths": [], "concerns": []}
    
    def find_best_suppliers(self, product_description: str, top_n: int = 10) -> List[Dict]:
        """Find the best suppliers for a complex product request"""
        print("Analyzing product requirements...")
        criteria = self.analyze_product_request(product_description)
        
        print(f"\nKey requirements identified:")
        print(f"- Product types: {', '.join(criteria['product_types'])}")
        print(f"- Certifications: {', '.join(criteria['certifications'])}")
        print(f"- Manufacturing: {', '.join(criteria['manufacturing_capabilities'])}")
        
        print("\nSearching database...")
        suppliers = self.search_suppliers(criteria)
        print(f"Found {len(suppliers)} potential suppliers")
        
        print("\nScoring suppliers with AI...")
        scored_suppliers = []
        
        for i, supplier in enumerate(suppliers[:50]):  # Score top 50 candidates
            if i % 10 == 0:
                print(f"  Scored {i}/{min(50, len(suppliers))} suppliers...")
            
            score_result = self.score_supplier(supplier, criteria, product_description)
            supplier['ai_score'] = score_result['score']
            supplier['match_reasons'] = score_result['reasons']
            supplier['strengths'] = score_result['strengths']
            supplier['concerns'] = score_result['concerns']
            
            if score_result['score'] > 40:  # Only keep relevant matches
                scored_suppliers.append(supplier)
        
        # Sort by score
        scored_suppliers.sort(key=lambda x: x['ai_score'], reverse=True)
        
        return scored_suppliers[:top_n]
    
    def close(self):
        self.cursor.close()
        self.conn.close()


# Interactive usage
if __name__ == "__main__":
    print("AI Supplier Search System Loaded Successfully!")
    print("=" * 50)
    print("Ready to search suppliers based on your product requirements.")
    print("Usage: searcher = AISupplierSearch()")
    print("       results = searcher.find_best_suppliers('your product description')")
    print("=" * 50)
    
    # Example function for interactive use
    def search_for_product(product_description: str, top_results: int = 10):
        """Search for suppliers matching your product requirements"""
        searcher = AISupplierSearch()
        
        try:
            best_suppliers = searcher.find_best_suppliers(product_description, top_n=top_results)
            
            print("\n" + "="*80)
            print(f"TOP {len(best_suppliers)} MATCHING SUPPLIERS")
            print("="*80)
            
            for i, supplier in enumerate(best_suppliers, 1):
                print(f"\n{i}. {supplier['supplier_name']} ({supplier['country']})")
                print(f"   Score: {supplier['ai_score']}/100")
                print(f"   Type: {supplier['supplier_type']}")
                print(f"   Contact: {supplier['company_email']}")
                if supplier['company_website']:
                    print(f"   Website: {supplier['company_website']}")
                
                print(f"\n   Strengths:")
                for strength in supplier['strengths']:
                    print(f"   + {strength}")
                
                if supplier['concerns']:
                    print(f"\n   Considerations:")
                    for concern in supplier['concerns']:
                        print(f"   - {concern}")
                
                print(f"\n   Products: {supplier['products'][:200]}...")
                print("-"*80)
            
            return best_suppliers
            
        finally:
            searcher.close()
    
    # Make function available globally
    globals()['search_for_product'] = search_for_product