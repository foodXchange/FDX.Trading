# Manual Fix Instructions for FoodXchange 503 Error

## Issue Summary
Your FoodXchange website (https://www.fdx.trading) has been down for over 1 day with a 503 Service Unavailable error.

## Manual Fix Steps

### Option 1: Via Kudu Console (Fastest)

1. **Access Kudu Console**
   - Go to: https://foodxchange-app.scm.azurewebsites.net
   - Login with your Azure credentials
   - If you get a 502 error, wait 5 minutes and try again

2. **Navigate to Debug Console**
   - Click "Debug console" → "CMD"
   - Navigate to: `D:\home\site\wwwroot`
   - Delete all existing files: `del /Q *.*`

3. **Create Minimal App Files**
   
   Create `app.py`:
   ```python
   from fastapi import FastAPI
   from datetime import datetime
   import os
   
   app = FastAPI()
   
   @app.get("/health")
   async def health():
       return {"status": "healthy", "timestamp": datetime.now().isoformat()}
   
   @app.get("/")
   async def root():
       return {"message": "FoodXchange API", "version": "1.0.0"}
   
   if __name__ == "__main__":
       import uvicorn
       port = int(os.environ.get("PORT", 8000))
       uvicorn.run("app:app", host="0.0.0.0", port=port)
   ```
   
   Create `requirements.txt`:
   ```
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   ```

4. **Set Startup Command**
   - In Azure Portal, go to your web app
   - Configuration → General settings
   - Startup Command: `python -m uvicorn app:app --host 0.0.0.0 --port 8000`
   - Save changes

5. **Restart the App**
   - In Azure Portal, click "Restart"

### Option 2: Via Azure Portal Deployment Center

1. **Reset Deployment**
   - Go to Azure Portal → Your Web App
   - Deployment Center → Disconnect
   - Wait 2 minutes
   - Set up "Local Git" deployment

2. **Create Local Repository**
   ```bash
   mkdir foodxchange-fix
   cd foodxchange-fix
   git init
   ```

3. **Add Minimal Files**
   - Copy the app.py and requirements.txt from Option 1
   - Add `.deployment` file:
   ```
   [config]
   SCM_DO_BUILD_DURING_DEPLOYMENT = true
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Minimal working app"
   git remote add azure <your-git-url>
   git push azure master
   ```

### Option 3: Emergency FTP Deploy

1. **Get FTP Credentials**
   - Azure Portal → Deployment Center → FTP
   - Note the FTP endpoint and credentials

2. **Connect via FTP**
   - Use FileZilla or similar
   - Navigate to /site/wwwroot
   - Delete all existing files
   - Upload the minimal app.py and requirements.txt

3. **Restart via Portal**

## Verification

After deployment, test these endpoints:
- https://foodxchange-app.azurewebsites.net/health
- https://www.fdx.trading/health

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-28T..."
}
```

## If Still Not Working

1. **Check Logs**
   ```bash
   az webapp log tail --name foodxchange-app --resource-group foodxchange-rg
   ```

2. **Scale Up Temporarily**
   - Change from B1 to S1 plan
   - Deploy
   - Scale back down

3. **Contact Support**
   - Open Azure support ticket
   - Reference deployment ID from Kudu

## Timeline
- Manual fix via Kudu: 10-15 minutes
- Git deployment: 20-30 minutes
- FTP deployment: 15-20 minutes

## Next Steps After Fix
Once the minimal app is working:
1. Deploy your full application
2. Update UptimeRobot to monitor the correct endpoint
3. Set up proper CI/CD pipeline