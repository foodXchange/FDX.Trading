# Simple Azure health fix
Write-Host "Creating minimal health endpoint fix..." -ForegroundColor Yellow

# Create app.py
@'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange</h1><p>Health: <a href="/health/simple">/health/simple</a></p>'

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/health/simple')
def health_simple():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
'@ | Out-File -FilePath "app.py" -Encoding UTF8

# Create requirements.txt
@'
Flask==3.0.0
gunicorn==21.2.0
'@ | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Create zip
Compress-Archive -Path @("app.py", "requirements.txt") -DestinationPath "health_fix.zip" -Force

# Deploy
Write-Host "Deploying..." -ForegroundColor Green
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path health_fix.zip --type zip

# Set startup
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "gunicorn --bind=0.0.0.0 app:app"

# Restart
az webapp restart --resource-group foodxchange-rg --name foodxchange-app

Write-Host "Done! Check https://www.fdx.trading/health/simple in 30 seconds" -ForegroundColor Green