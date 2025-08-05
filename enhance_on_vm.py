#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv
import openai
from datetime import datetime
import time
import sys

# Load environment variables
load_dotenv()

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"

print("🚀 Enhancing Remaining Suppliers on VM\n")

def generate_product_description(supplier_name, country, supplier_type, existing_products):
    """Generate enhanced product description using Azure OpenAI"""
    
    prompt = f"""Based on this supplier information, generate a detailed product catalog:
Supplier: {supplier_name}
Country: {country}
Type: {supplier_type if supplier_type else 'Food supplier'}
Current Products: {existing_products if existing_products and len(str(existing_products)) > 10 else 'Not specified'}

Generate a comprehensive list of likely products and services this supplier offers.
Include specific product categories, certifications, and specialties.
Make it realistic based on the supplier name and country.
Format: Clear, comma-separated list of products and services.
Length: 200-300 characters."""

    try:
        response = openai.ChatCompletion.create(
            deployment_id=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a food industry expert creating detailed supplier catalogs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  ⚠️  Fallback for {supplier_name}: {str(e)[:50]}...")
        # Enhanced fallback
        base_products = {
            'italy': 'Pasta, olive oil, tomatoes, cheese, wine, balsamic vinegar, prosciutto, Italian specialties',
            'spain': 'Olive oil, jamón, cheese, wine, seafood, paella ingredients, Spanish delicacies',
            'netherlands': 'Cheese, dairy products, vegetables, flowers, processed foods, Dutch specialties',
            'united states': 'Processed foods, snacks, beverages, meat products, dairy, American food products',
            'russia': 'Grains, dairy, meat products, preserved foods, Russian specialties',
            'greece': 'Olive oil, feta cheese, olives, yogurt, honey, Greek specialties',
            'thailand': 'Rice, coconut products, spices, seafood, Thai ingredients, Asian specialties',
            'france': 'Cheese, wine, bakery products, gourmet foods, French delicacies',
            'germany': 'Meat products, beer, bread, dairy, German specialties',
            'turkey': 'Nuts, dried fruits, spices, Turkish delight, Mediterranean products'
        }
        
        country_lower = country.lower() if country else ''
        default_products = base_products.get(country_lower, 'Various food products, ingredients, and specialties')
        
        if supplier_type and len(str(supplier_type)) > 5:
            return f"{supplier_type} offering {default_products}"
        else:
            return f"Food supplier from {country} specializing in {default_products}"

try:
    # Connect to database
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Get count of suppliers needing enhancement
    cur.execute("""
        SELECT COUNT(*) 
        FROM suppliers 
        WHERE products IS NULL OR LENGTH(products) <= 200
    """)
    total_to_enhance = cur.fetchone()[0]
    
    print(f"📊 Found {total_to_enhance:,} suppliers needing enhancement\n")
    
    if total_to_enhance == 0:
        print("✅ All suppliers are already enhanced!")
        sys.exit(0)
    
    # Process in smaller batches to avoid timeouts
    batch_size = 50
    enhanced_count = 0
    error_count = 0
    start_time = datetime.now()
    
    while enhanced_count < total_to_enhance:
        # Get batch of unenhanced suppliers
        cur.execute("""
            SELECT id, supplier_name, country, supplier_type, products
            FROM suppliers 
            WHERE products IS NULL OR LENGTH(products) <= 200
            LIMIT %s
        """, (batch_size,))
        
        suppliers = cur.fetchall()
        
        if not suppliers:
            break
        
        print(f"\n🔄 Processing batch of {len(suppliers)} suppliers...")
        
        # Prepare updates
        updates = []
        batch_errors = 0
        
        for supplier_id, name, country, supplier_type, existing_products in suppliers:
            try:
                # Generate enhanced description
                enhanced_products = generate_product_description(
                    name, country, supplier_type, existing_products
                )
                
                updates.append((enhanced_products, datetime.now(), supplier_id))
                enhanced_count += 1
                
            except Exception as e:
                batch_errors += 1
                error_count += 1
                # Use fallback for this supplier
                fallback = f"Food supplier from {country} offering various products and services"
                updates.append((fallback, datetime.now(), supplier_id))
                enhanced_count += 1
            
            # Show progress every 10 suppliers
            if enhanced_count % 10 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = enhanced_count / (elapsed + 1)
                remaining = total_to_enhance - enhanced_count
                eta = remaining / rate if rate > 0 else 0
                
                print(f"✅ Enhanced {enhanced_count:,}/{total_to_enhance:,} suppliers "
                      f"({enhanced_count*100//total_to_enhance}%) - "
                      f"Rate: {rate:.1f}/s - "
                      f"ETA: {int(eta//60)}m {int(eta%60)}s")
        
        # Batch update
        if updates:
            execute_batch(cur, """
                UPDATE suppliers 
                SET products = %s, updated_at = %s 
                WHERE id = %s
            """, updates)
            
            conn.commit()
            print(f"  💾 Saved batch of {len(updates)} suppliers (Errors: {batch_errors})")
        
        # Small delay to avoid rate limits
        time.sleep(2)
    
    # Final statistics
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN products IS NOT NULL AND LENGTH(products) > 200 THEN 1 END) as enhanced
        FROM suppliers
    """)
    total, enhanced = cur.fetchone()
    
    print(f"\n🎉 Enhancement Complete!")
    print(f"📊 Final Status: {enhanced:,}/{total:,} suppliers enhanced ({enhanced*100//total}%)")
    print(f"⚠️  Total API errors handled: {error_count}")
    
    # Show sample enhanced suppliers
    cur.execute("""
        SELECT supplier_name, products 
        FROM suppliers 
        WHERE updated_at > NOW() - INTERVAL '1 hour'
        ORDER BY updated_at DESC 
        LIMIT 3
    """)
    
    print("\n📦 Sample Enhanced Suppliers:")
    for name, products in cur.fetchall():
        print(f"\n{name}:")
        print(f"{products[:150]}..." if len(products) > 150 else products)
    
    cur.close()
    conn.close()
    
    elapsed_total = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️ Total time: {int(elapsed_total//60)}m {int(elapsed_total%60)}s")
    print(f"📈 Average rate: {enhanced_count/elapsed_total:.1f} suppliers/second")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()