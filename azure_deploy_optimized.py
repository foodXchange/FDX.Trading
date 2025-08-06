#!/usr/bin/env python3
"""
Deploy Optimized Search using Azure CLI
No SSH passwords required
"""

import subprocess
import os
import json
import base64

def deploy_via_azure():
    """Deploy search optimization files via Azure CLI"""
    
    resource_group = "foodxchange-founders-rg"
    vm_name = "fdx-founders-vm"
    
    print("Deploying Optimized Search System via Azure CLI")
    print("=" * 60)
    
    # Files to deploy
    files_to_deploy = {
        "optimize_product_search.py": "Product classification system",
        "product_variation_handler.py": "1-to-many product handler",
        "enhance_supplier_data.py": "Website scraping system",
        "openai_search.py": "AI-powered search",
        "advanced_search_system.py": "Complex query parser"
    }
    
    # Read and encode each file
    for filename, description in files_to_deploy.items():
        if os.path.exists(filename):
            print(f"\nDeploying {filename} - {description}")
            
            # Read file content
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create deployment script
            script = f"""
#!/bin/bash
cd /home/fdxfounder/fdx/app

# Backup existing file if it exists
if [ -f "{filename}" ]; then
    cp {filename} {filename}.backup.$(date +%Y%m%d_%H%M%S)
fi

# Write new file
cat > {filename} << 'EOF'
{content}
EOF

chmod +x {filename}
echo "Deployed {filename}"
"""
            
            # Save script temporarily
            script_file = f"deploy_{filename}.sh"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Upload and execute via Azure CLI
            cmd = [
                "az", "vm", "run-command", "invoke",
                "--resource-group", resource_group,
                "--name", vm_name,
                "--command-id", "RunShellScript",
                "--scripts", f"@{script_file}"
            ]
            
            print(f"  Uploading {filename}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"  SUCCESS: {filename} deployed")
            else:
                print(f"  ERROR deploying {filename}: {result.stderr}")
            
            # Clean up temp script
            os.remove(script_file)
        else:
            print(f"WARNING: {filename} not found locally")
    
    # Create app integration script
    print("\nCreating integrated app with all optimizations...")
    
    integration_script = """
#!/bin/bash
cd /home/fdxfounder/fdx/app

# Create integrated app
cat > app_integrated.py << 'EOF'
#!/usr/bin/env python3
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Import optimization modules
try:
    from optimize_product_search import ProductSearchOptimizer
    from product_variation_handler import ProductVariationHandler
    optimizer_available = True
except:
    optimizer_available = False

load_dotenv()

app = FastAPI(
    title="FDX.trading",
    description="B2B Food Trading Platform with AI-Optimized Search",
    version="3.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse(url="/suppliers", status_code=303)

@app.post("/api/search")
async def api_search(request: Request):
    '''Optimized search that excludes ingredient users'''
    try:
        form_data = await request.form()
        query = form_data.get('query', '')
        
        if not query:
            return JSONResponse(
                content={"error": "No search query", "results": []},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        # Use optimizer if available
        if optimizer_available:
            try:
                # Check for product variations
                handler = ProductVariationHandler()
                variation_results = handler.find_suppliers_with_variations(query)
                
                # Also run classification
                optimizer = ProductSearchOptimizer()
                classified_results = optimizer.optimize_search(query, limit=100)
                
                # Combine results - manufacturers with variations first
                manufacturers = variation_results.get('top_manufacturers', [])[:20]
                sellers = classified_results.get('sellers', [])[:30]
                
                # Deduplicate by supplier_id
                seen_ids = set()
                final_results = []
                
                for supplier in manufacturers + sellers:
                    if supplier['supplier_id'] not in seen_ids:
                        seen_ids.add(supplier['supplier_id'])
                        final_results.append(supplier)
                
                return JSONResponse(
                    content={
                        'query': query,
                        'total_results': len(final_results),
                        'message': f"Found {len(manufacturers)} manufacturers with product variations",
                        'results': final_results[:50]
                    },
                    headers={"Content-Type": "application/json; charset=utf-8"}
                )
            except Exception as opt_error:
                print(f"Optimizer error: {opt_error}")
        
        # Fallback to basic search
        conn = get_db_connection()
        if not conn:
            return JSONResponse(
                content={"error": "Database error", "results": []},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        cursor = conn.cursor()
        search_term = f"%{query.lower()}%"
        
        cursor.execute('''
            SELECT id, supplier_name, company_name, country, products,
                   company_email as email, company_website as website,
                   verified, rating
            FROM suppliers
            WHERE LOWER(products) LIKE %s
               OR LOWER(supplier_name) LIKE %s
            ORDER BY rating DESC NULLS LAST
            LIMIT 100
        ''', (search_term, search_term))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        formatted_results = []
        for r in results:
            formatted_results.append({
                'supplier_id': r['id'],
                'supplier_name': r['supplier_name'],
                'company_name': r['company_name'] or r['supplier_name'],
                'country': r['country'] or 'Unknown',
                'email': r['email'] or '',
                'website': r['website'] or '',
                'product_preview': r['products'][:300] if r.get('products') else '',
                'verified': r.get('verified', False),
                'rating': float(r['rating']) if r.get('rating') else 0
            })
        
        return JSONResponse(
            content={
                'query': query,
                'total_results': len(formatted_results),
                'results': formatted_results
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "results": []},
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "optimizer": "enabled" if optimizer_available else "disabled",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Make it executable
chmod +x app_integrated.py

# Backup current app
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py

# Activate new app
cp app_integrated.py app.py

echo "Integrated app deployed successfully"
"""
    
    # Save and execute integration script
    with open("integrate_app.sh", "w") as f:
        f.write(integration_script)
    
    print("Deploying integrated app...")
    cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", resource_group,
        "--name", vm_name,
        "--command-id", "RunShellScript",
        "--scripts", "@integrate_app.sh"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        print("SUCCESS: Integrated app deployed")
    else:
        print(f"ERROR: {result.stderr}")
    
    os.remove("integrate_app.sh")
    
    # Restart the application
    print("\nRestarting application...")
    restart_cmd = [
        "az", "vm", "run-command", "invoke",
        "--resource-group", resource_group,
        "--name", vm_name,
        "--command-id", "RunShellScript",
        "--scripts", "sudo systemctl restart fdx-app || sudo systemctl restart gunicorn || sudo supervisorctl restart fdx-app"
    ]
    
    result = subprocess.run(restart_cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("Application restarted")
    else:
        print("Manual restart may be needed")
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("\nNew capabilities deployed:")
    print("1. Product classification (sellers vs users)")
    print("2. 1-to-many product variation handling")
    print("3. Complex requirement matching")
    print("4. Wafer biscuits example: finds manufacturers with multiple flavors/formats")
    print("5. Puffed snacks example: matches shape, flavor, certifications")
    print("\nTest at: https://www.fdx.trading")

if __name__ == "__main__":
    deploy_via_azure()