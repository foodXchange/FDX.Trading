# Fast batch enhancement with better error handling
import os
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import time
from datetime import datetime
import sys

load_dotenv()

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

DATABASE_URL = "postgresql://fdxadmin:FDX2030!@foodxchange-flex-db.postgres.database.azure.com:5432/foodxchange?sslmode=require"

client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

print("=== FAST BATCH ENHANCEMENT ===\n")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Get stats
cursor.execute("""
    SELECT COUNT(*) FROM suppliers 
    WHERE products IS NULL OR LENGTH(COALESCE(products, '')) < 10
""")
remaining = cursor.fetchone()[0]

print(f"Suppliers to enhance: {remaining:,}")
print("Processing in large batches...\n")

start_time = datetime.now()
total_enhanced = 0
BATCH_SIZE = 20  # Process 20 at once

while remaining > 0:
    # Get batch
    cursor.execute("""
        SELECT id, supplier_name, country, supplier_type
        FROM suppliers 
        WHERE products IS NULL OR LENGTH(COALESCE(products, '')) < 10
        ORDER BY id
        LIMIT %s
    """, (BATCH_SIZE,))
    
    suppliers = cursor.fetchall()
    if not suppliers:
        break
    
    updates = []
    
    for supplier in suppliers:
        id, name, country, type_info = supplier
        
        try:
            # Simple prompt for speed
            prompt = f"{name} from {country}. List 10 specific food products:"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.9
            )
            
            products = response.choices[0].message.content.strip()
            
            if len(products) > 20:
                # Enhanced type based on country/name
                if country in ['Italy', 'Spain', 'Greece']:
                    type_enhanced = f"Mediterranean Food {type_info or 'Supplier'}"
                elif country in ['China', 'Japan', 'Korea']:
                    type_enhanced = f"Asian Food {type_info or 'Supplier'}"
                else:
                    type_enhanced = f"International Food {type_info or 'Supplier'}"
                
                updates.append((products, type_enhanced, id))
                total_enhanced += 1
                
        except Exception as e:
            continue
    
    # Batch update
    if updates:
        execute_batch(
            cursor,
            "UPDATE suppliers SET products = %s, supplier_type = %s WHERE id = %s",
            updates,
            page_size=100
        )
        conn.commit()
    
    # Progress
    elapsed = (datetime.now() - start_time).total_seconds()
    rate = total_enhanced / (elapsed / 60) if elapsed > 0 else 0
    eta = remaining / rate if rate > 0 else 0
    
    print(f"Enhanced: {total_enhanced} | Rate: {rate:.1f}/min | ETA: {eta:.1f} min | Remaining: {remaining}")
    
    remaining -= len(suppliers)
    
    # Brief pause
    time.sleep(0.5)

# Final stats
elapsed = (datetime.now() - start_time).total_seconds() / 60
print(f"\nCOMPLETE!")
print(f"Total enhanced: {total_enhanced:,}")
print(f"Time: {elapsed:.1f} minutes")
print(f"Average rate: {total_enhanced/elapsed:.1f} suppliers/minute")

cursor.close()
conn.close()