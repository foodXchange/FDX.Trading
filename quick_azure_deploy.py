#!/usr/bin/env python3
"""
Quick Azure Deployment Fix
Deploys a minimal working FastAPI app to fix 503 errors
"""

import os
import subprocess
import zipfile
import sys
import time

print("Quick Azure Deployment Fix")
print("=" * 50)

# Create minimal working app
app_content = '''from fastapi import FastAPI, Response
from datetime import datetime
import os

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "FoodXchange API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.head("/health")
async def health_head():
    return Response(status_code=200)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''

requirements_content = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
'''

startup_content = '''#!/bin/bash
echo "Starting FoodXchange minimal app..."
python -m uvicorn app:app --host 0.0.0.0 --port $PORT
'''

# Create files
print("\nCreating deployment files...")
with open("app.py", "w") as f:
    f.write(app_content)
print("[OK] Created app.py")

with open("requirements.txt", "w") as f:
    f.write(requirements_content)
print("[OK] Created requirements.txt")

with open("startup.sh", "w") as f:
    f.write(startup_content)
print("[OK] Created startup.sh")

# Create deployment package
print("\nCreating deployment package...")
zip_name = "azure_quick_fix.zip"
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write("app.py")
    zipf.write("requirements.txt")
    zipf.write("startup.sh")
print(f"[OK] Created {zip_name}")

# Deploy to Azure
print("\nDeploying to Azure...")
print("This will take 2-3 minutes...")

cmd = f"az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path {zip_name} --type zip --restart true"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print("[SUCCESS] Deployment successful!")
    
    # Set startup command
    print("\nSetting startup command...")
    cmd = 'az webapp config set --name foodxchange-app --resource-group foodxchange-rg --startup-file "python -m uvicorn app:app --host 0.0.0.0 --port 8000"'
    subprocess.run(cmd, shell=True)
    
    # Restart app
    print("\nRestarting app...")
    cmd = "az webapp restart --name foodxchange-app --resource-group foodxchange-rg"
    subprocess.run(cmd, shell=True)
    
    print("\nWaiting for app to start (60 seconds)...")
    time.sleep(60)
    
    # Test the app
    print("\nTesting deployment...")
    import requests
    try:
        response = requests.get("https://foodxchange-app.azurewebsites.net/health", timeout=10)
        if response.status_code == 200:
            print("[SUCCESS] App is working!")
            print(f"Response: {response.json()}")
        else:
            print(f"[WARNING] App returned status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
    
    print("\nDeployment Summary:")
    print("- URL: https://foodxchange-app.azurewebsites.net")
    print("- Health: https://foodxchange-app.azurewebsites.net/health")
    print("- Kudu: https://foodxchange-app.scm.azurewebsites.net")
    
else:
    print("[ERROR] Deployment failed!")
    print(result.stderr)
    print("\nTrying alternative deployment method...")
    
    # Try with az webapp deployment
    cmd = f"az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange-app --src {zip_name}"
    result2 = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result2.returncode == 0:
        print("[SUCCESS] Alternative deployment successful!")
    else:
        print("[ERROR] Alternative deployment also failed")
        print(result2.stderr)