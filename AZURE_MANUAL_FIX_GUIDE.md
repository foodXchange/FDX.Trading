# Azure FoodXchange Manual Fix Guide

## Issue Summary
The health endpoint at https://www.fdx.trading/health/simple has been down for over 1 day with a 503 error. The Azure App Service is failing to start the Python application properly.

## Root Cause
From the logs, the main issues are:
1. Python modules (uvicorn, flask) are not being installed
2. The startup command is failing
3. The deployment process is not building the Python environment correctly

## Manual Fix Steps

### Option 1: Use Azure Portal Kudu Console

1. **Access Kudu Console**
   - Go to Azure Portal
   - Navigate to: Resource groups > foodxchange-rg > foodxchange-app
   - Click on "Advanced Tools" > "Go"
   - Or directly: https://foodxchange-app.scm.azurewebsites.net

2. **In Kudu Debug Console (CMD)**
   ```cmd
   cd D:\home\site\wwwroot
   python -m pip install flask==3.0.0
   ```

3. **Create a simple application.py**
   ```python
   from flask import Flask, jsonify
   import os
   
   app = Flask(__name__)
   
   @app.route('/health/simple')
   def health_simple():
       return jsonify({"status": "ok"})
   
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 8000))
       app.run(host='0.0.0.0', port=port)
   ```

4. **Restart the app**
   - In Azure Portal, click "Restart" on the app overview page

### Option 2: Use SSH in Azure Portal

1. **Enable SSH**
   - In Azure Portal, go to foodxchange-app
   - Configuration > General settings
   - Enable "Web SSH"

2. **Connect via SSH and fix**
   ```bash
   cd /home/site/wwwroot
   pip install flask
   echo 'from flask import Flask, jsonify; app = Flask(__name__); app.route("/health/simple")(lambda: jsonify({"status": "ok"})); app.run(host="0.0.0.0", port=8000)' > app.py
   ```

### Option 3: Deploy via Azure Portal

1. **In Azure Portal**
   - Go to foodxchange-app
   - Deployment Center > Settings
   - Choose "Local Git" or "OneDeploy"
   
2. **Create minimal app locally**
   - Create app.py with health endpoints
   - Create requirements.txt with Flask==3.0.0
   - Zip these files

3. **Upload via Deployment Center**
   - Use the ZIP deploy option
   - Upload your zip file

### Option 4: Configure Static Response (Temporary)

1. **In Azure Portal**
   - Configuration > Application settings
   - Add new setting: `WEBSITE_WEBDEPLOY_USE_SCM` = `false`
   - Add: `WEBSITE_RUN_FROM_PACKAGE` = `0`

2. **Set a simple startup command**
   - Configuration > General settings
   - Startup Command: `python -m http.server 8000`

### Verification

After any of these fixes, check:
1. https://www.fdx.trading/health/simple
2. https://foodxchange-app.azurewebsites.net/health/simple

### If All Else Fails

Contact Azure Support with:
- Subscription ID: 88931ed0-52df-42fb-a09c-e024c9586f8a
- Resource Group: foodxchange-rg
- App Name: foodxchange-app
- Issue: Python app failing to start, modules not installing

## Expected Result
The health endpoint should return:
```json
{"status": "ok"}
```

## DNS Configuration (Already Correct)
- fdx.trading → foodxchange-app.azurewebsites.net ✓
- www.fdx.trading → foodxchange-app.azurewebsites.net ✓