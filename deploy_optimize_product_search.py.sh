
#!/bin/bash
cd /home/fdxfounder/fdx/app

# Backup existing file if it exists
if [ -f "optimize_product_search.py" ]; then
    cp optimize_product_search.py optimize_product_search.py.backup.$(date +%Y%m%d_%H%M%S)
fi

# Write new file
cat > optimize_product_search.py << 'EOF'
#!/usr/bin/env python3
"""
Optimize Product Search for FDX.trading
Ensures search returns suppliers who SELL the product, not use it as ingredient
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class ProductSearchOptimizer:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        
        # Keywords that indicate a supplier SELLS the product (not uses it)
        self.seller_indicators = [
            'manufacturer', 'producer', 'supplier', 'exporter', 'distributor',
            'wholesale', 'trading', 'oils', 'mill', 'refinery', 'production',
            'export', 'supply', 'bottles', 'bulk', 'containers', 'packaging'
        ]
        
        # Keywords that indicate a supplier USES the product as ingredient
        self.user_indicators = [
            'bakery', 'cookies', 'cakes', 'crackers', 'snacks', 'chips',
            'restaurant', 'catering', 'confectionery', 'chocolate', 'candy',
            'prepared foods', 'ready meals', 'frozen meals', 'pizza', 'pasta dishes'
        ]
        
        # Product-specific seller patterns
        self.oil_seller_patterns = [
            r'\b\d+L\b', r'\b\d+ml\b',  # Size indicators (1L, 500ml)
            r'\bbottles?\b', r'\bcontainers?\b', r'\bbulk\b',
            r'\brefined\b', r'\bcrude\b', r'\bvirgin\b',
            r'\bedible oils?\b', r'\bcooking oils?\b',
            r'\boil company\b', r'\boil factory\b', r'\boil producer\b'
        ]
    
    def classify_supplier(self, supplier_data):
        """
        Classify if supplier SELLS or USES a product
        Returns: 'seller', 'user', or 'unknown'
        """
        products = (supplier_data.get('products') or '').lower()
        supplier_name = (supplier_data.get('supplier_name') or '').lower()
        supplier_type = (supplier_data.get('supplier_type') or '').lower()
        
        seller_score = 0
        user_score = 0
        
        # Check supplier type
        for indicator in self.seller_indicators:
            if indicator in supplier_type or indicator in supplier_name:
                seller_score += 10
        
        for indicator in self.user_indicators:
            if indicator in supplier_type or indicator in supplier_name:
                user_score += 10
        
        # Check product description
        for indicator in self.seller_indicators:
            if indicator in products:
                seller_score += 5
        
        for indicator in self.user_indicators:
            if indicator in products:
                user_score += 5
        
        # Check for oil-specific patterns
        for pattern in self.oil_seller_patterns:
            if re.search(pattern, products):
                seller_score += 8
        
        # Decision logic
        if seller_score > user_score * 1.5:
            return 'seller'
        elif user_score > seller_score * 1.5:
            return 'user'
        else:
            return 'unknown'
    
    def optimize_search(self, product_query, limit=50):
        """
        Search for suppliers who SELL the product, not use it
        """
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Step 1: Get all potential matches
        search_term = f"%{product_query.lower()}%"
        
        cur.execute("""
            SELECT id, supplier_name, company_name, country, products,
                   company_email, company_website, supplier_type, verified, rating
            FROM suppliers
            WHERE LOWER(products) LIKE %s
               OR LOWER(supplier_name) LIKE %s
            LIMIT 500
        """, (search_term, search_term))
        
        all_results = cur.fetchall()
        
        # Step 2: Classify and filter
        sellers = []
        users = []
        unknown = []
        
        for supplier in all_results:
            classification = self.classify_supplier(supplier)
            
            result = {
                'supplier_id': supplier['id'],
                'supplier_name': supplier['supplier_name'],
                'company_name': supplier['company_name'] or supplier['supplier_name'],
                'country': supplier['country'] or 'Unknown',
                'email': supplier['company_email'] or '',
                'website': supplier['company_website'] or '',
                'products': supplier['products'] or '',
                'product_preview': (supplier['products'] or '')[:300],
                'supplier_type': supplier['supplier_type'] or '',
                'verified': supplier.get('verified', False),
                'rating': float(supplier['rating']) if supplier.get('rating') else None,
                'classification': classification
            }
            
            if classification == 'seller':
                sellers.append(result)
            elif classification == 'user':
                users.append(result)
            else:
                unknown.append(result)
        
        # Step 3: Rank sellers by relevance
        for seller in sellers:
            score = 100
            products_lower = seller['products'].lower()
            
            # Exact product match
            if product_query.lower() in products_lower:
                score += 50
            
            # Check for size/packaging mentions
            if re.search(r'\b\d+L\b|\b\d+ml\b|\bbottles?\b', products_lower):
                score += 30
            
            # Verified suppliers get bonus
            if seller['verified']:
                score += 20
            
            # Rating bonus
            if seller['rating']:
                score += seller['rating'] * 5
            
            seller['relevance_score'] = score
        
        # Sort by relevance
        sellers.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        cur.close()
        conn.close()
        
        return {
            'query': product_query,
            'total_sellers': len(sellers),
            'total_users': len(users),
            'total_unknown': len(unknown),
            'sellers': sellers[:limit],
            'excluded_users': users[:10]  # Show what we filtered out
        }
    
    def add_product_classification_column(self):
        """Add a column to store supplier classification"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        
        try:
            # Add column if it doesn't exist
            cur.execute("""
                ALTER TABLE suppliers 
                ADD COLUMN IF NOT EXISTS product_classification VARCHAR(50)
            """)
            
            # Add index for faster searches
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_classification 
                ON suppliers(product_classification)
            """)
            
            conn.commit()
            print("Added product_classification column")
            
        except Exception as e:
            print(f"Error adding column: {e}")
            conn.rollback()
        
        cur.close()
        conn.close()
    
    def classify_all_suppliers(self):
        """Classify all suppliers in database (one-time operation)"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Process in batches
        offset = 0
        batch_size = 100
        total_classified = 0
        
        while True:
            cur.execute("""
                SELECT id, supplier_name, products, supplier_type
                FROM suppliers
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (batch_size, offset))
            
            batch = cur.fetchall()
            if not batch:
                break
            
            for supplier in batch:
                classification = self.classify_supplier(supplier)
                
                # Update classification
                cur.execute("""
                    UPDATE suppliers 
                    SET product_classification = %s
                    WHERE id = %s
                """, (classification, supplier['id']))
            
            conn.commit()
            total_classified += len(batch)
            print(f"Classified {total_classified} suppliers...")
            
            offset += batch_size
        
        cur.close()
        conn.close()
        
        print(f"Finished classifying {total_classified} suppliers")

# FastAPI endpoint
def create_optimized_search_endpoint(app):
    """Add optimized search endpoint to FastAPI app"""
    
    @app.post("/api/optimized-search")
    async def optimized_search(request):
        from fastapi.responses import JSONResponse
        
        form_data = await request.form()
        query = form_data.get('query', '')
        
        if not query:
            return JSONResponse(
                content={"error": "No query provided", "sellers": []},
                status_code=400
            )
        
        optimizer = ProductSearchOptimizer()
        results = optimizer.optimize_search(query)
        
        # Format for frontend
        formatted_results = {
            'query': query,
            'total_results': results['total_sellers'],
            'message': f"Found {results['total_sellers']} suppliers who SELL {query} (excluded {results['total_users']} who use it as ingredient)",
            'results': results['sellers']
        }
        
        return JSONResponse(
            content=formatted_results,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

if __name__ == "__main__":
    # Test the optimizer
    optimizer = ProductSearchOptimizer()
    
    # Add classification column
    print("Setting up database optimization...")
    optimizer.add_product_classification_column()
    
    # Test search
    print("\nTesting optimized search for 'sunflower oil'...")
    results = optimizer.optimize_search("sunflower oil", limit=10)
    
    print(f"\nResults Summary:")
    print(f"- Suppliers who SELL sunflower oil: {results['total_sellers']}")
    print(f"- Suppliers who USE it as ingredient: {results['total_users']}")
    print(f"- Unknown classification: {results['total_unknown']}")
    
    if results['sellers']:
        print(f"\nTop 3 SELLERS of sunflower oil:")
        for i, seller in enumerate(results['sellers'][:3], 1):
            print(f"\n{i}. {seller['supplier_name']} ({seller['country']})")
            print(f"   Products: {seller['product_preview'][:150]}...")
            print(f"   Classification: {seller['classification']}")
    
    if results['excluded_users']:
        print(f"\nExcluded suppliers (use as ingredient):")
        for user in results['excluded_users'][:3]:
            print(f"- {user['supplier_name']}: {user['product_preview'][:100]}...")
EOF

chmod +x optimize_product_search.py
echo "Deployed optimize_product_search.py"
