#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import time
import sys

# Load environment variables
load_dotenv()

print("🚀 Enhanced Supplier Enhancement Script for VM\n")

# Azure OpenAI configuration
api_key = os.getenv("AZURE_OPENAI_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

# Build the API URL
api_url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version=2023-05-15"

def generate_product_description_azure(supplier_name, country, supplier_type, existing_products):
    """Generate enhanced product description using Azure OpenAI REST API"""
    
    prompt = f"""Based on this supplier information, generate a detailed product catalog:
Supplier: {supplier_name}
Country: {country}
Type: {supplier_type if supplier_type else 'Food supplier'}
Current Products: {existing_products if existing_products and len(str(existing_products)) > 10 else 'Not specified'}

Generate a comprehensive list of likely products and services this supplier offers.
Include specific product categories, certifications, and specialties.
Make it realistic based on the supplier name and country.
Format: Clear, comma-separated list of products and services.
Length: 250-400 characters."""

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    data = {
        "messages": [
            {"role": "system", "content": "You are a food industry expert creating detailed supplier catalogs."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 400,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"  ⚠️  API Error {response.status_code} for {supplier_name}")
            raise Exception(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"  ⚠️  Error for {supplier_name}: {str(e)[:50]}...")
        # Enhanced fallback based on country and type
        return generate_fallback_description(supplier_name, country, supplier_type)

def generate_fallback_description(supplier_name, country, supplier_type):
    """Generate intelligent fallback descriptions based on supplier data"""
    
    # Country-specific product templates
    country_products = {
        'italy': 'Pasta, olive oil, tomatoes, cheese, wine, balsamic vinegar, prosciutto, pizza ingredients, Italian herbs, canned goods, artisanal products',
        'spain': 'Olive oil, jamón ibérico, manchego cheese, wine, paella ingredients, saffron, paprika, gazpacho, tapas products, Spanish preserves',
        'netherlands': 'Gouda cheese, dairy products, vegetables, flowers, stroopwafels, chocolate, processed foods, greenhouse produce',
        'united states': 'Processed foods, snacks, beverages, meat products, dairy, condiments, frozen foods, organic products',
        'russia': 'Grains, dairy products, preserved foods, caviar, vodka, buckwheat, sunflower oil, Russian specialties',
        'greece': 'Olive oil, feta cheese, olives, yogurt, honey, herbs, seafood, Greek wines, Mediterranean specialties',
        'thailand': 'Rice, coconut products, curry paste, fish sauce, tropical fruits, seafood, Thai spices, noodles',
        'france': 'Cheese varieties, wine, champagne, foie gras, bakery products, gourmet foods, French delicacies',
        'germany': 'Sausages, beer, bread, pretzels, sauerkraut, mustard, dairy products, German specialties',
        'turkey': 'Nuts, dried fruits, Turkish delight, baklava, olive oil, spices, tea, Mediterranean products',
        'china': 'Rice, soy products, tea, noodles, sauces, preserved vegetables, seafood, Asian ingredients',
        'india': 'Spices, rice, lentils, tea, curry powders, chutneys, pickles, Indian sweets',
        'mexico': 'Corn products, chili peppers, beans, tequila, tortillas, salsa, Mexican spices',
        'japan': 'Sushi ingredients, soy sauce, miso, sake, noodles, seafood, Japanese specialties',
        'brazil': 'Coffee, açaí, tropical fruits, meat products, cassava, Brazilian nuts, guarana'
    }
    
    # Type-specific additions
    type_products = {
        'manufacturer': 'production, packaging, private label services',
        'distributor': 'logistics, warehousing, supply chain solutions',
        'importer': 'international sourcing, customs clearance',
        'exporter': 'export documentation, international shipping',
        'producer': 'farming, harvesting, processing',
        'wholesaler': 'bulk sales, B2B services',
        'trader': 'commodity trading, market access'
    }
    
    # Get base products for country
    country_lower = country.lower() if country else ''
    base_products = country_products.get(country_lower, 'Various food products, ingredients, and culinary specialties')
    
    # Add type-specific services
    type_lower = supplier_type.lower() if supplier_type else ''
    additional_services = ''
    for key, value in type_products.items():
        if key in type_lower:
            additional_services = f', {value}'
            break
    
    # Build description based on supplier name hints
    name_lower = supplier_name.lower() if supplier_name else ''
    
    # Check for specific product hints in name
    if 'olive' in name_lower:
        base_products = f'Extra virgin olive oil, organic olive oil, olives, {base_products}'
    elif 'cheese' in name_lower or 'dairy' in name_lower:
        base_products = f'Artisanal cheeses, dairy products, milk, yogurt, {base_products}'
    elif 'wine' in name_lower or 'vineyard' in name_lower:
        base_products = f'Premium wines, grape products, wine accessories, {base_products}'
    elif 'chocolate' in name_lower or 'cocoa' in name_lower:
        base_products = f'Chocolate products, cocoa, confectionery, {base_products}'
    elif 'coffee' in name_lower:
        base_products = f'Coffee beans, roasted coffee, coffee products, {base_products}'
    elif 'spice' in name_lower:
        base_products = f'Spices, seasonings, spice blends, {base_products}'
    elif 'meat' in name_lower:
        base_products = f'Meat products, processed meats, fresh meats, {base_products}'
    elif 'fish' in name_lower or 'seafood' in name_lower:
        base_products = f'Fresh seafood, frozen fish, seafood products, {base_products}'
    elif 'bakery' in name_lower or 'bread' in name_lower:
        base_products = f'Bakery products, bread, pastries, baked goods, {base_products}'
    elif 'fruit' in name_lower:
        base_products = f'Fresh fruits, dried fruits, fruit products, {base_products}'
    
    # Construct final description
    final_description = f"{base_products}{additional_services}"
    
    # Ensure minimum length
    if len(final_description) < 200:
        final_description += f". Specializing in {country} food products with focus on quality and tradition"
    
    return final_description[:400]  # Limit to 400 chars

try:
    # Test Azure OpenAI connection
    print("🔧 Testing Azure OpenAI connection...")
    test_desc = generate_product_description_azure("Test Supplier", "Italy", "Manufacturer", "")
    if len(test_desc) > 50:
        print("✅ Azure OpenAI connection successful!\n")
    else:
        print("⚠️  Azure OpenAI returned short response, will use enhanced fallbacks\n")
    
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
    
    # Process in smaller batches
    batch_size = 25  # Smaller batches for better progress tracking
    enhanced_count = 0
    api_success_count = 0
    fallback_count = 0
    start_time = datetime.now()
    
    while enhanced_count < total_to_enhance:
        # Get batch of unenhanced suppliers
        cur.execute("""
            SELECT id, supplier_name, country, supplier_type, products
            FROM suppliers 
            WHERE products IS NULL OR LENGTH(products) <= 200
            ORDER BY id
            LIMIT %s
        """, (batch_size,))
        
        suppliers = cur.fetchall()
        
        if not suppliers:
            break
        
        print(f"\n🔄 Processing batch of {len(suppliers)} suppliers...")
        
        # Prepare updates
        updates = []
        
        for supplier_id, name, country, supplier_type, existing_products in suppliers:
            # Generate enhanced description
            enhanced_products = generate_product_description_azure(
                name, country, supplier_type, existing_products
            )
            
            # Track if API or fallback was used
            if "Food supplier from" in enhanced_products or "Various food products" in enhanced_products:
                fallback_count += 1
            else:
                api_success_count += 1
            
            updates.append((enhanced_products, datetime.now(), supplier_id))
            enhanced_count += 1
            
            # Show progress every 5 suppliers
            if enhanced_count % 5 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = enhanced_count / (elapsed + 1)
                remaining = total_to_enhance - enhanced_count
                eta = remaining / rate if rate > 0 else 0
                
                print(f"✅ Progress: {enhanced_count:,}/{total_to_enhance:,} ({enhanced_count*100//total_to_enhance}%)")
                print(f"   API: {api_success_count} | Fallback: {fallback_count} | "
                      f"Rate: {rate:.1f}/s | ETA: {int(eta//60)}m {int(eta%60)}s")
        
        # Batch update
        if updates:
            execute_batch(cur, """
                UPDATE suppliers 
                SET products = %s, updated_at = %s 
                WHERE id = %s
            """, updates, page_size=100)
            
            conn.commit()
            print(f"💾 Saved batch of {len(updates)} suppliers")
        
        # Small delay to avoid rate limits
        time.sleep(1)
    
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
    print(f"📈 API Success: {api_success_count} | Smart Fallbacks: {fallback_count}")
    
    # Show sample enhanced suppliers
    cur.execute("""
        SELECT supplier_name, country, products 
        FROM suppliers 
        WHERE updated_at > NOW() - INTERVAL '1 hour'
        ORDER BY updated_at DESC 
        LIMIT 5
    """)
    
    print("\n📦 Sample Enhanced Suppliers:")
    for name, country, products in cur.fetchall():
        print(f"\n{name} ({country}):")
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