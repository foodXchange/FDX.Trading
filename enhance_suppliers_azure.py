# Azure OpenAI-powered supplier data enhancement
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import time
from typing import Dict, List

load_dotenv()

# Azure OpenAI configuration
client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

class SupplierEnhancer:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
    def get_all_suppliers(self, limit=None):
        """Get all suppliers from database"""
        query = "SELECT * FROM suppliers"
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_suppliers_needing_enhancement(self):
        """Get suppliers missing key data"""
        query = """
        SELECT * FROM suppliers 
        WHERE products IS NULL 
           OR LENGTH(COALESCE(products, '')) < 10
           OR supplier_type IS NULL
           OR LENGTH(COALESCE(supplier_type, '')) < 20
        ORDER BY id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def enhance_supplier_with_ai(self, supplier: Dict) -> Dict:
        """Use Azure OpenAI to enhance supplier data"""
        # Build context about the supplier
        context_parts = []
        if supplier['supplier_name']:
            context_parts.append(f"Company: {supplier['supplier_name']}")
        if supplier['supplier_type']:
            context_parts.append(f"Current Type: {supplier['supplier_type']}")
        if supplier['country']:
            context_parts.append(f"Country: {supplier['country']}")
        if supplier['company_website']:
            context_parts.append(f"Website: {supplier['company_website']}")
        if supplier['products']:
            context_parts.append(f"Current Products: {supplier['products']}")
            
        context = "\n".join(context_parts)
        
        prompt = f"""
        Analyze this food industry supplier and provide enhanced data:
        
        {context}
        
        Return a JSON object with these fields:
        {{
            "products": "Comprehensive list of likely products they supply (comma-separated)",
            "supplier_type_enhanced": "Detailed supplier category (e.g., 'Premium Olive Oil Producer and Exporter')",
            "business_focus": "Main business focus in 20-30 words",
            "likely_certifications": "Likely certifications (ISO, HACCP, Organic, etc.)",
            "export_capabilities": "Yes/No/Unknown",
            "company_size_estimate": "Small (1-50) / Medium (51-500) / Large (500+)"
        }}
        
        Base your analysis on the company name, country, and any available information.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using your deployed model
                messages=[
                    {"role": "system", "content": "You are a food industry expert analyzing supplier data. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    enhanced_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found")
            except:
                # Fallback if JSON parsing fails
                enhanced_data = {
                    "products": "Food products",
                    "supplier_type_enhanced": supplier['supplier_type'] or "Food supplier",
                    "business_focus": "Food industry supplier",
                    "likely_certifications": "",
                    "export_capabilities": "Unknown",
                    "company_size_estimate": "Unknown"
                }
            
            return enhanced_data
            
        except Exception as e:
            print(f"Error enhancing supplier {supplier['id']}: {e}")
            return None
    
    def update_supplier(self, supplier_id: int, enhanced_data: Dict):
        """Update supplier with enhanced data"""
        try:
            updates = []
            params = []
            
            # Update products if enhanced
            if enhanced_data.get('products') and len(enhanced_data['products']) > 10:
                updates.append("products = %s")
                params.append(enhanced_data['products'])
            
            # Update supplier type if enhanced
            if enhanced_data.get('supplier_type_enhanced') and len(enhanced_data['supplier_type_enhanced']) > 20:
                updates.append("supplier_type = %s")
                params.append(enhanced_data['supplier_type_enhanced'])
            
            if updates:
                params.append(supplier_id)
                query = f"UPDATE suppliers SET {', '.join(updates)} WHERE id = %s"
                self.cursor.execute(query, params)
                self.conn.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating supplier {supplier_id}: {e}")
            self.conn.rollback()
            return False
    
    def enhance_batch(self, batch_size=10):
        """Enhance suppliers in batches"""
        suppliers = self.get_suppliers_needing_enhancement()[:batch_size]
        total = len(suppliers)
        print(f"Processing batch of {total} suppliers")
        
        enhanced_count = 0
        for i, supplier in enumerate(suppliers):
            print(f"\n[{i+1}/{total}] Processing: {supplier['supplier_name']}")
            
            enhanced_data = self.enhance_supplier_with_ai(supplier)
            if enhanced_data:
                if self.update_supplier(supplier['id'], enhanced_data):
                    enhanced_count += 1
                    print(f"  [OK] Enhanced successfully")
                    if enhanced_data.get('products'):
                        print(f"    Products: {enhanced_data['products'][:100]}...")
                    if enhanced_data.get('supplier_type_enhanced'):
                        print(f"    Type: {enhanced_data['supplier_type_enhanced']}")
                else:
                    print(f"  - No updates needed")
            else:
                print(f"  [X] Enhancement failed")
            
            # Rate limiting (Azure OpenAI has generous limits but let's be safe)
            time.sleep(0.5)
        
        print(f"\n[DONE] Enhanced {enhanced_count} suppliers")
        return enhanced_count
    
    def get_enhancement_stats(self):
        """Get statistics on data enhancement needs"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN products IS NULL OR LENGTH(products) < 10 THEN 1 END) as need_products,
                COUNT(CASE WHEN supplier_type IS NULL OR LENGTH(supplier_type) < 20 THEN 1 END) as need_type,
                COUNT(CASE WHEN products IS NOT NULL AND LENGTH(products) >= 10 THEN 1 END) as have_products
            FROM suppliers
        """)
        return self.cursor.fetchone()
    
    def close(self):
        """Close database connections"""
        self.cursor.close()
        self.conn.close()


# Run the enhancement
if __name__ == "__main__":
    print("=== Azure OpenAI Supplier Enhancement ===\n")
    
    enhancer = SupplierEnhancer()
    
    # Show current stats
    stats = enhancer.get_enhancement_stats()
    print(f"Database Statistics:")
    print(f"- Total suppliers: {stats['total']:,}")
    print(f"- Need product data: {stats['need_products']:,}")
    print(f"- Need better type data: {stats['need_type']:,}")
    print(f"- Already have products: {stats['have_products']:,}")
    
    print("\nOptions:")
    print("1. Enhance 10 suppliers (test)")
    print("2. Enhance 100 suppliers")
    print("3. Enhance 1000 suppliers")
    print("4. Show sample of enhanced data")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == "1":
        enhancer.enhance_batch(10)
        
    elif choice == "2":
        confirm = input("This will make ~100 API calls. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            enhancer.enhance_batch(100)
            
    elif choice == "3":
        confirm = input("This will make ~1000 API calls. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            # Process in batches of 100
            for i in range(10):
                print(f"\n=== Batch {i+1}/10 ===")
                enhancer.enhance_batch(100)
                if i < 9:
                    print("Pausing 5 seconds between batches...")
                    time.sleep(5)
                    
    elif choice == "4":
        # Show some already enhanced suppliers
        enhancer.cursor.execute("""
            SELECT supplier_name, products, supplier_type 
            FROM suppliers 
            WHERE products IS NOT NULL 
              AND LENGTH(products) > 50
            LIMIT 5
        """)
        
        print("\nSample of enhanced suppliers:")
        for row in enhancer.cursor.fetchall():
            print(f"\n{row['supplier_name']}")
            print(f"  Type: {row['supplier_type']}")
            print(f"  Products: {row['products'][:150]}...")
    
    enhancer.close()
    print("\nDone!")