# Enhanced script to process ALL suppliers with progress tracking
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import time
from datetime import datetime
import sys

load_dotenv()

# Azure OpenAI configuration
client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

class BulkSupplierEnhancer:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.start_time = datetime.now()
        self.total_enhanced = 0
        self.total_failed = 0
        
    def get_suppliers_to_enhance(self):
        """Get count of suppliers needing enhancement"""
        query = """
        SELECT COUNT(*) as count
        FROM suppliers 
        WHERE products IS NULL 
           OR LENGTH(COALESCE(products, '')) < 10
           OR supplier_type IS NULL
           OR LENGTH(COALESCE(supplier_type, '')) < 20
        """
        self.cursor.execute(query)
        return self.cursor.fetchone()['count']
    
    def get_batch_to_enhance(self, batch_size=100):
        """Get next batch of suppliers to enhance"""
        query = """
        SELECT * FROM suppliers 
        WHERE products IS NULL 
           OR LENGTH(COALESCE(products, '')) < 10
           OR supplier_type IS NULL
           OR LENGTH(COALESCE(supplier_type, '')) < 20
        ORDER BY id
        LIMIT %s
        """
        self.cursor.execute(query, (batch_size,))
        return self.cursor.fetchall()
    
    def enhance_supplier(self, supplier):
        """Enhance a single supplier"""
        context_parts = []
        if supplier['supplier_name']:
            context_parts.append(f"Company: {supplier['supplier_name']}")
        if supplier['supplier_type']:
            context_parts.append(f"Current Type: {supplier['supplier_type']}")
        if supplier['country']:
            context_parts.append(f"Country: {supplier['country']}")
        if supplier['company_website']:
            context_parts.append(f"Website: {supplier['company_website']}")
            
        context = "\n".join(context_parts)
        
        prompt = f"""
        Analyze this food industry supplier and provide enhanced data:
        
        {context}
        
        Return a JSON object with:
        {{
            "products": "Comprehensive list of likely products (comma-separated, at least 5-10 products)",
            "supplier_type_enhanced": "Detailed supplier category (20-40 words)"
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a food industry expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            return None
            
        except Exception as e:
            print(f"    Error: {e}")
            return None
    
    def update_supplier(self, supplier_id, data):
        """Update supplier in database"""
        try:
            updates = []
            params = []
            
            if data.get('products') and len(data['products']) > 10:
                updates.append("products = %s")
                params.append(data['products'])
            
            if data.get('supplier_type_enhanced') and len(data['supplier_type_enhanced']) > 20:
                updates.append("supplier_type = %s")
                params.append(data['supplier_type_enhanced'])
            
            if updates:
                params.append(supplier_id)
                query = f"UPDATE suppliers SET {', '.join(updates)} WHERE id = %s"
                self.cursor.execute(query, params)
                return True
            return False
            
        except Exception as e:
            print(f"    Update error: {e}")
            return False
    
    def process_all(self, batch_size=100):
        """Process all suppliers in batches"""
        total_to_process = self.get_suppliers_to_enhance()
        print(f"Total suppliers to enhance: {total_to_process:,}\n")
        
        if total_to_process == 0:
            print("No suppliers need enhancement!")
            return
        
        # Confirm before starting
        estimated_time = (total_to_process * 0.6) / 60  # ~0.6 seconds per supplier
        print(f"Estimated time: {estimated_time:.1f} minutes")
        print(f"Estimated API calls: {total_to_process:,}")
        print(f"Estimated cost: ${total_to_process * 0.00015:.2f}\n")
        
        confirm = input("Proceed with enhancement? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled")
            return
        
        print("\nStarting enhancement process...\n")
        
        processed = 0
        while processed < total_to_process:
            # Get next batch
            batch = self.get_batch_to_enhance(batch_size)
            if not batch:
                break
            
            batch_start = datetime.now()
            print(f"[Batch {processed//batch_size + 1}] Processing {len(batch)} suppliers...")
            
            enhanced_in_batch = 0
            for i, supplier in enumerate(batch):
                # Show progress every 10 suppliers
                if i % 10 == 0 and i > 0:
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    rate = self.total_enhanced / elapsed if elapsed > 0 else 0
                    eta = (total_to_process - processed) / rate if rate > 0 else 0
                    print(f"  Progress: {processed + i}/{total_to_process} ({(processed + i)*100//total_to_process}%) - ETA: {eta/60:.1f} min")
                
                # Enhance supplier
                enhanced_data = self.enhance_supplier(supplier)
                if enhanced_data:
                    if self.update_supplier(supplier['id'], enhanced_data):
                        enhanced_in_batch += 1
                        self.total_enhanced += 1
                else:
                    self.total_failed += 1
                
                # Small delay to avoid rate limits
                time.sleep(0.3)
            
            # Commit batch
            self.conn.commit()
            
            batch_time = (datetime.now() - batch_start).total_seconds()
            print(f"  Batch complete: {enhanced_in_batch} enhanced in {batch_time:.1f}s\n")
            
            processed += len(batch)
            
            # Pause between batches
            if processed < total_to_process:
                time.sleep(2)
        
        # Final summary
        total_time = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*50)
        print("ENHANCEMENT COMPLETE!")
        print("="*50)
        print(f"Total processed: {processed:,}")
        print(f"Successfully enhanced: {self.total_enhanced:,}")
        print(f"Failed: {self.total_failed:,}")
        print(f"Total time: {total_time/60:.1f} minutes")
        print(f"Average rate: {self.total_enhanced/(total_time/60):.1f} suppliers/minute")
        
        # Show sample of enhanced data
        print("\nSample of enhanced suppliers:")
        self.cursor.execute("""
            SELECT supplier_name, products, supplier_type 
            FROM suppliers 
            WHERE products IS NOT NULL 
              AND LENGTH(products) > 50
            ORDER BY id DESC
            LIMIT 3
        """)
        
        for row in self.cursor.fetchall():
            print(f"\n{row['supplier_name']}")
            print(f"  Type: {row['supplier_type']}")
            print(f"  Products: {row['products'][:100]}...")
    
    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    print("=== BULK SUPPLIER ENHANCEMENT ===\n")
    
    enhancer = BulkSupplierEnhancer()
    
    try:
        enhancer.process_all(batch_size=100)
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        print(f"Enhanced {enhancer.total_enhanced} suppliers before stopping")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        enhancer.close()