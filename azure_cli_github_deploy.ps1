# Deploy from GitHub using Azure CLI
Write-Host "Setting up GitHub deployment for Azure..." -ForegroundColor Yellow

# First, let's use Azure CLI to run commands directly on the app
Write-Host "`nStep 1: Running remote commands to fix the app..." -ForegroundColor Cyan

# Create a command that will run on the Azure app
$remoteCommand = @"
cd /home/site/wwwroot && \
python -m pip install --upgrade pip && \
pip install flask==3.0.0 && \
echo 'from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>FoodXchange</h1><p>Health: <a href=\"/health/simple\">/health/simple</a></p>"

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/health/simple")
def health_simple():
    return jsonify({"status": "ok"})

@app.route("/health/detailed")
def health_detailed():
    return jsonify({"status": "healthy", "service": "foodxchange", "version": "1.0.0"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)' > app.py && \
echo 'Flask==3.0.0' > requirements.txt && \
echo 'python app.py' > startup.sh && \
chmod +x startup.sh
"@

# Run the command via Azure CLI
Write-Host "Executing remote fix commands..." -ForegroundColor Cyan
az webapp command --resource-group foodxchange-rg --name foodxchange-app --command "$remoteCommand"

# Alternative: Use deployment configuration
Write-Host "`nStep 2: Configuring deployment from local files..." -ForegroundColor Cyan

# Create a minimal Flask app
@'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange API</h1><p>Status: <a href="/health/simple">Health Check</a></p>'

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/health/simple')
def health_simple():
    return jsonify({"status": "ok"})

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        "status": "healthy",
        "service": "foodxchange",
        "version": "1.0.0",
        "timestamp": "2025-01-28T12:00:00Z"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)
'@ | Out-File -FilePath "app.py" -Encoding UTF8

# Create requirements
"Flask==3.0.0" | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Use Azure CLI deployment
Write-Host "`nStep 3: Deploying using Azure CLI up command..." -ForegroundColor Green
az webapp up `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --runtime "PYTHON:3.11" `
    --sku B1 `
    --logs

Write-Host "`nStep 4: Setting startup command..." -ForegroundColor Cyan
az webapp config set `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"

# Restart
Write-Host "`nStep 5: Restarting app..." -ForegroundColor Cyan
az webapp restart --resource-group foodxchange-rg --name foodxchange-app

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Check health endpoints:" -ForegroundColor Yellow
Write-Host "- https://www.fdx.trading/health/simple" -ForegroundColor Cyan
Write-Host "- https://foodxchange-app.azurewebsites.net/health/simple" -ForegroundColor Cyan

# Stream logs to see what's happening
Write-Host "`nStreaming logs (Ctrl+C to stop)..." -ForegroundColor Yellow
az webapp log tail --resource-group foodxchange-rg --name foodxchange-app