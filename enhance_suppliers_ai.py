# AI-powered supplier data enhancement
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import openai
import json
import time
from typing import Dict, List

load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')  # You'll need to add this to .env

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
           OR LENGTH(products) < 10
           OR supplier_type IS NULL
           OR LENGTH(supplier_type) < 10
        ORDER BY id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def enhance_supplier_with_ai(self, supplier: Dict) -> Dict:
        """Use OpenAI to enhance supplier data"""
        prompt = f"""
        Based on this supplier information, provide enhanced data:
        
        Company: {supplier['supplier_name']}
        Current Type: {supplier['supplier_type']}
        Country: {supplier['country']}
        Website: {supplier['company_website']}
        
        Please provide in JSON format:
        1. products: Detailed list of likely products (comma-separated)
        2. supplier_type_enhanced: More detailed supplier type/category
        3. business_description: Brief business description (50-100 words)
        4. certifications_likely: Likely certifications based on country/type
        5. export_markets: Likely export markets
        6. company_size: Estimated size (small/medium/large)
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a food industry expert helping enhance supplier data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            try:
                enhanced_data = json.loads(content)
            except:
                # If not valid JSON, create structured data from response
                enhanced_data = {
                    "products": "Food products",
                    "supplier_type_enhanced": supplier['supplier_type'] or "Food supplier",
                    "business_description": content[:200],
                    "certifications_likely": "",
                    "export_markets": "",
                    "company_size": "medium"
                }
            
            return enhanced_data
            
        except Exception as e:
            print(f"Error enhancing supplier {supplier['id']}: {e}")
            return None
    
    def update_supplier(self, supplier_id: int, enhanced_data: Dict):
        """Update supplier with enhanced data"""
        try:
            # Update existing fields
            if enhanced_data.get('products'):
                self.cursor.execute(
                    "UPDATE suppliers SET products = %s WHERE id = %s",
                    (enhanced_data['products'], supplier_id)
                )
            
            # You can add more fields to update here
            self.conn.commit()
            
        except Exception as e:
            print(f"Error updating supplier {supplier_id}: {e}")
            self.conn.rollback()
    
    def enhance_batch(self, batch_size=10):
        """Enhance suppliers in batches"""
        suppliers = self.get_suppliers_needing_enhancement()
        total = len(suppliers)
        print(f"Found {total} suppliers needing enhancement")
        
        enhanced_count = 0
        for i in range(0, min(batch_size, total)):
            supplier = suppliers[i]
            print(f"\nProcessing {i+1}/{batch_size}: {supplier['supplier_name']}")
            
            enhanced_data = self.enhance_supplier_with_ai(supplier)
            if enhanced_data:
                self.update_supplier(supplier['id'], enhanced_data)
                enhanced_count += 1
                print(f"  ✓ Enhanced successfully")
            else:
                print(f"  ✗ Enhancement failed")
            
            # Rate limiting
            time.sleep(1)  # Avoid hitting API rate limits
        
        print(f"\nEnhanced {enhanced_count} suppliers")
        return enhanced_count
    
    def export_all_data(self, filename='suppliers_full.csv'):
        """Export all supplier data to CSV"""
        import pandas as pd
        
        query = "SELECT * FROM suppliers ORDER BY id"
        df = pd.read_sql(query, self.conn)
        df.to_csv(filename, index=False)
        print(f"Exported {len(df)} suppliers to {filename}")
        return filename
    
    def close(self):
        """Close database connections"""
        self.cursor.close()
        self.conn.close()


# Example usage
if __name__ == "__main__":
    print("=== Supplier Data Enhancement Tool ===\n")
    
    # Check if OpenAI key is configured
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: Please add OPENAI_API_KEY to your .env file")
        print("Get your API key from: https://platform.openai.com/api-keys")
        exit(1)
    
    enhancer = SupplierEnhancer()
    
    # Show options
    print("Options:")
    print("1. Show database statistics")
    print("2. Enhance suppliers with AI (batch of 10)")
    print("3. Export all data to CSV")
    print("4. Process all suppliers (WARNING: This will use many API calls)")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == "1":
        # Show stats
        suppliers = enhancer.get_all_suppliers()
        need_enhancement = enhancer.get_suppliers_needing_enhancement()
        print(f"\nTotal suppliers: {len(suppliers)}")
        print(f"Need enhancement: {len(need_enhancement)}")
        
    elif choice == "2":
        # Enhance batch
        enhancer.enhance_batch(10)
        
    elif choice == "3":
        # Export all
        filename = enhancer.export_all_data()
        print(f"Data exported to: {filename}")
        
    elif choice == "4":
        # Process all (with confirmation)
        need_enhancement = enhancer.get_suppliers_needing_enhancement()
        total = len(need_enhancement)
        
        print(f"\nThis will process {total} suppliers")
        print(f"Estimated API calls: {total}")
        print(f"Estimated cost: ${total * 0.002:.2f} (at ~$0.002 per call)")
        
        confirm = input("\nProceed? (yes/no): ")
        if confirm.lower() == "yes":
            batch_size = 100
            for i in range(0, total, batch_size):
                print(f"\nProcessing batch {i//batch_size + 1}")
                enhancer.enhance_batch(batch_size)
                time.sleep(5)  # Pause between batches
    
    enhancer.close()
    print("\nDone!")