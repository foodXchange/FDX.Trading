# Process 1000 suppliers at a time
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import time
from datetime import datetime

load_dotenv()

client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

BATCH_LIMIT = 1000  # Process 1000 suppliers per run

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Check remaining
cursor.execute("""
    SELECT COUNT(*) as count
    FROM suppliers 
    WHERE products IS NULL OR LENGTH(COALESCE(products, '')) < 10
""")
remaining = cursor.fetchone()['count']

if remaining == 0:
    print("All suppliers have been enhanced!")
    cursor.close()
    conn.close()
    exit(0)

print(f"\nSuppliers remaining: {remaining:,}")
print(f"Processing next {min(BATCH_LIMIT, remaining)} suppliers...\n")

start_time = datetime.now()
enhanced = 0
failed = 0

# Get suppliers to process
cursor.execute("""
    SELECT id, supplier_name, supplier_type, country, company_website
    FROM suppliers 
    WHERE products IS NULL OR LENGTH(COALESCE(products, '')) < 10
    ORDER BY id
    LIMIT %s
""", (BATCH_LIMIT,))

suppliers = cursor.fetchall()

for i, supplier in enumerate(suppliers):
    try:
        # Build context
        name = supplier['supplier_name'] or 'Unknown'
        country = supplier['country'] or 'Unknown'
        type_info = supplier['supplier_type'] or ''
        
        # Create prompt
        prompt = f"""Food supplier: {name} from {country}
Type: {type_info}

Return JSON with:
- products: list of 8-15 specific products this supplier likely offers
- type: enhanced supplier category (20-30 words)"""

        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a food industry expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=250
        )
        
        # Parse and update
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            data = json.loads(content[start_idx:end_idx])
            
            products = data.get('products', '')
            new_type = data.get('type', supplier['supplier_type'])
            
            if products and len(products) > 10:
                cursor.execute(
                    "UPDATE suppliers SET products = %s, supplier_type = %s WHERE id = %s",
                    (products, new_type, supplier['id'])
                )
                enhanced += 1
                
                # Show progress
                if enhanced % 50 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    rate = enhanced / (elapsed / 60) if elapsed > 0 else 0
                    print(f"Progress: {i+1}/{len(suppliers)} - Enhanced: {enhanced} - Rate: {rate:.1f}/min")
    
    except Exception as e:
        failed += 1
        if failed % 20 == 0:
            print(f"  Errors: {failed} (latest: {str(e)[:50]})")
    
    # Small delay to avoid rate limits
    if i % 10 == 0:
        time.sleep(0.2)

# Commit all changes
conn.commit()

# Summary
elapsed = (datetime.now() - start_time).total_seconds()
print(f"\nBatch complete in {elapsed/60:.1f} minutes")
print(f"Enhanced: {enhanced}")
print(f"Failed: {failed}")
print(f"Success rate: {enhanced*100//(enhanced+failed) if enhanced+failed > 0 else 0}%")

# Check total progress
cursor.execute("""
    SELECT COUNT(*) as enhanced
    FROM suppliers 
    WHERE products IS NOT NULL AND LENGTH(products) > 10
""")
total_enhanced = cursor.fetchone()['enhanced']
print(f"\nTotal enhanced so far: {total_enhanced:,} / 18,031 ({total_enhanced*100//18031}%)")

cursor.close()
conn.close()

# Exit with status 0 if more to process, 1 if done
exit(0 if remaining > BATCH_LIMIT else 1)