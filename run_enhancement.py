# Simple continuous enhancement with live progress
import os
import psycopg2
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import time
from datetime import datetime

load_dotenv()

# Hardcode the database URL
DATABASE_URL = "postgresql://fdxadmin:FDX2030!@foodxchange-flex-db.postgres.database.azure.com:5432/foodxchange?sslmode=require"

client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

print("SUPPLIER ENHANCEMENT RUNNING...")
print("Press Ctrl+C to stop\n")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Get initial stats
cursor.execute("SELECT COUNT(*) FROM suppliers WHERE products IS NOT NULL AND LENGTH(products) > 10")
already_enhanced = cursor.fetchone()[0]
print(f"Starting point: {already_enhanced:,} suppliers already enhanced\n")

enhanced_this_session = 0
start_time = datetime.now()

try:
    while True:
        # Get next supplier
        cursor.execute("""
            SELECT id, supplier_name, country, supplier_type
            FROM suppliers 
            WHERE products IS NULL OR LENGTH(COALESCE(products, '')) < 10
            ORDER BY id
            LIMIT 1
        """)
        
        supplier = cursor.fetchone()
        if not supplier:
            print("\nALL SUPPLIERS ENHANCED!")
            break
        
        id, name, country, type_info = supplier
        
        # Enhance
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user", 
                    "content": f"Food supplier {name} from {country}. List 10 specific products they likely offer. Reply with just the comma-separated list."
                }],
                max_tokens=150
            )
            
            products = response.choices[0].message.content.strip()
            
            if len(products) > 10:
                cursor.execute(
                    "UPDATE suppliers SET products = %s WHERE id = %s",
                    (products, id)
                )
                conn.commit()
                
                enhanced_this_session += 1
                total = already_enhanced + enhanced_this_session
                
                # Show progress
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                rate = enhanced_this_session / elapsed if elapsed > 0 else 0
                
                print(f"\r[{total:,}/18,031] {name[:40]:40} | Rate: {rate:.1f}/min", end='', flush=True)
                
                if enhanced_this_session % 50 == 0:
                    print(f"\n  Milestone: {enhanced_this_session} enhanced this session!")
                    
        except Exception as e:
            print(f"\n  Error with {name}: {str(e)[:50]}")
        
        # Small delay
        time.sleep(0.3)
        
except KeyboardInterrupt:
    print("\n\nStopped by user")
    
finally:
    elapsed = (datetime.now() - start_time).total_seconds() / 60
    print(f"\nSession Summary:")
    print(f"- Enhanced this session: {enhanced_this_session}")
    print(f"- Total enhanced: {already_enhanced + enhanced_this_session:,}")
    print(f"- Time: {elapsed:.1f} minutes")
    print(f"- Rate: {enhanced_this_session/elapsed:.1f} suppliers/minute")
    
    cursor.close()
    conn.close()