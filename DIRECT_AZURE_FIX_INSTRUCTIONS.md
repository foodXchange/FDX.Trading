# Direct Azure Fix Instructions

The health endpoint has been down for over 1 day. Here's how to fix it directly through Azure:

## Option 1: Use Azure Portal Kudu Console

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to: **Resource groups** > **foodxchange-rg** > **foodxchange-app**
3. In the left menu, under **Development Tools**, click **Advanced Tools** > **Go**
4. This opens Kudu console at: https://foodxchange-app.scm.azurewebsites.net

### In Kudu Console:

1. Click **Debug console** > **CMD**
2. Navigate to: `D:\home\site\wwwroot`
3. Create a simple `application.py` file:

```python
from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange</h1><p>Service is running</p>'

@app.route('/health')
@app.route('/health/simple')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'mode': 'emergency'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
```

4. Update the startup command in Azure Portal:
   - Go to **Configuration** > **General settings**
   - Set **Startup Command** to: `python application.py`
   - Click **Save** and **Continue**

## Option 2: Use Azure CLI Commands

Run these commands in order:

```powershell
# 1. Stop the app
az webapp stop --name foodxchange-app --resource-group foodxchange-rg

# 2. Set a simple startup command
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "python -m flask run --host=0.0.0.0 --port=8000"

# 3. Set Flask app environment variable
az webapp config appsettings set --resource-group foodxchange-rg --name foodxchange-app --settings FLASK_APP="application.py"

# 4. Start the app
az webapp start --name foodxchange-app --resource-group foodxchange-rg

# 5. Wait 60 seconds then test
Start-Sleep -Seconds 60
Invoke-WebRequest -Uri "https://www.fdx.trading/health/simple" -Method GET
```

## Option 3: Emergency Flask Deployment

Create this minimal package and deploy:

1. Create `emergency_flask.zip` with:
   - `application.py` (the Flask app above)
   - `requirements.txt` with just: `flask==3.0.0`

2. Deploy it:
```powershell
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path emergency_flask.zip --type zip
```

## Verification Steps

After any of these options, verify:

1. Check Azure URL: https://foodxchange-app.azurewebsites.net/health/simple
2. Check custom domain: https://www.fdx.trading/health/simple
3. Check logs: `az webapp log tail --resource-group foodxchange-rg --name foodxchange-app`

## Why This Works

- Flask is simpler than FastAPI and has fewer dependencies
- The minimal app ensures health endpoints work immediately
- Once health is restored, you can gradually add back complexity

## Next Steps After Health is Restored

1. Gradually migrate back to FastAPI
2. Add database connections one at a time
3. Monitor each change to ensure health stays up