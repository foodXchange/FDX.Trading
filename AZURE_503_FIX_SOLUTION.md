# Azure Web App 503 Error - Comprehensive Solution

## Problem Summary
Your FoodXchange website (https://www.fdx.trading) is showing a 503 Service Unavailable error. The Azure Web App is running but not responding to requests.

## Root Causes
1. **Deployment conflicts**: There's an ongoing deployment blocking new deployments
2. **Startup command issues**: The current startup configuration isn't working properly
3. **Missing environment variables**: Several critical app settings are null
4. **Python environment**: Azure is having trouble with the Python 3.12 runtime

## Solution Steps

### Step 1: Stop Current Deployment (2 minutes)
```powershell
# Stop the current deployment
az webapp stop --name foodxchange-app --resource-group foodxchange-rg

# Wait 30 seconds
Start-Sleep -Seconds 30

# Start the app again
az webapp start --name foodxchange-app --resource-group foodxchange-rg
```

### Step 2: Configure App Settings (3 minutes)
```powershell
# Set critical environment variables
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    WEBSITES_PORT=8000 `
    PYTHON_VERSION=3.12 `
    ENVIRONMENT=production `
    SECRET_KEY="your-secret-key-here"
```

### Step 3: Deploy Minimal Working App (5 minutes)

Create a file named `minimal_app.py`:
```python
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="FoodXchange")

@app.get("/")
def root():
    return {"message": "FoodXchange API", "timestamp": datetime.now().isoformat()}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

Create `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
```

### Step 4: Deploy via Kudu Console (5 minutes)
1. Navigate to: https://foodxchange-app.scm.azurewebsites.net
2. Go to Debug Console > CMD
3. Navigate to: `site\wwwroot`
4. Delete all existing files
5. Upload the minimal files:
   - minimal_app.py (rename to app.py)
   - requirements.txt

### Step 5: Set Startup Command (2 minutes)
```powershell
az webapp config set --name foodxchange-app --resource-group foodxchange-rg `
    --startup-file "python -m uvicorn app:app --host 0.0.0.0 --port 8000"
```

### Step 6: Restart and Verify (3 minutes)
```powershell
# Restart the app
az webapp restart --name foodxchange-app --resource-group foodxchange-rg

# Wait for restart
Start-Sleep -Seconds 60

# Test the health endpoint
Invoke-WebRequest -Uri "https://foodxchange-app.azurewebsites.net/health" -TimeoutSec 10
```

## Alternative: SSH Direct Fix (10 minutes)

If the above doesn't work, use SSH:

```powershell
# Enable SSH
az webapp config set --name foodxchange-app --resource-group foodxchange-rg --remote-debugging-enabled true

# Get SSH credentials
az webapp create-remote-connection --name foodxchange-app --resource-group foodxchange-rg --port 2222
```

Then in SSH:
```bash
cd /home/site/wwwroot
rm -rf *
echo 'from fastapi import FastAPI; app = FastAPI(); app.get("/health")(lambda: {"status": "healthy"})' > app.py
echo 'fastapi==0.104.1' > requirements.txt
echo 'uvicorn[standard]==0.24.0' >> requirements.txt
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Timeline
- **Immediate** (0-5 min): Stop/start app, configure settings
- **Quick** (5-10 min): Deploy minimal app via Kudu
- **Verification** (10-15 min): Test endpoints and confirm working

## Verification
Once deployed, these endpoints should work:
- https://foodxchange-app.azurewebsites.net/health → {"status": "healthy", "timestamp": "..."}
- https://foodxchange-app.azurewebsites.net/ → {"message": "FoodXchange API", "timestamp": "..."}

## DNS Configuration (if needed)
Ensure your DNS has these records:
- **Type**: CNAME
- **Host**: www
- **Value**: foodxchange-app.azurewebsites.net
- **TTL**: 3600

## Next Steps After Fix
1. Deploy the full application incrementally
2. Set up proper monitoring with Azure Application Insights
3. Configure automated health checks
4. Set up deployment slots for zero-downtime deployments

## Emergency Contacts
- Azure Support: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- Kudu Console: https://foodxchange-app.scm.azurewebsites.net
- Azure Portal: https://portal.azure.com/#@/resource/subscriptions/88931ed0-52df-42fb-a09c-e024c9586f8a/resourceGroups/foodxchange-rg/providers/Microsoft.Web/sites/foodxchange-app