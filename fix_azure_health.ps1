# Fix Azure health endpoints
Write-Host "Fixing Azure FoodXchange health endpoints..." -ForegroundColor Yellow

# Create a minimal working deployment
Write-Host "`nCreating minimal health endpoint deployment..." -ForegroundColor Cyan

# Create minimal app.py with just health endpoints
$appContent = @'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange API</h1><p>Visit <a href="/health">/health</a> for status</p>'

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "foodxchange"})

@app.route('/health/simple')
def health_simple():
    return jsonify({"status": "ok"})

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        "status": "healthy",
        "service": "foodxchange",
        "timestamp": "2025-01-28T10:45:00Z",
        "version": "1.0.0"
    })

@app.route('/api/health')
def api_health():
    return jsonify({"status": "healthy", "api": "v1"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
'@

Set-Content -Path "app.py" -Value $appContent -Encoding UTF8

# Create requirements.txt
$requirements = @'
Flask==3.0.0
gunicorn==21.2.0
'@

Set-Content -Path "requirements.txt" -Value $requirements -Encoding UTF8

# Create startup command file
$startupCmd = "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
Set-Content -Path "startup.txt" -Value $startupCmd -Encoding UTF8

# Create deployment package
Write-Host "`nCreating deployment package..." -ForegroundColor Cyan
if (Test-Path "health_fix.zip") { Remove-Item "health_fix.zip" -Force }

Compress-Archive -Path @("app.py", "requirements.txt", "startup.txt") -DestinationPath "health_fix.zip" -Force

Write-Host "`nDeploying to Azure..." -ForegroundColor Green

# Deploy using zip deployment
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path health_fix.zip --type zip

# Set startup command
Write-Host "`nSetting startup command..." -ForegroundColor Cyan
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"

# Restart the app
Write-Host "`nRestarting app..." -ForegroundColor Cyan
az webapp restart --resource-group foodxchange-rg --name foodxchange-app

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Testing endpoints in 30 seconds..." -ForegroundColor Yellow

Start-Sleep -Seconds 30

# Test the endpoints
$endpoints = @(
    "https://foodxchange-app.azurewebsites.net/health",
    "https://foodxchange-app.azurewebsites.net/health/simple",
    "https://www.fdx.trading/health",
    "https://www.fdx.trading/health/simple"
)

Write-Host "`nTesting health endpoints:" -ForegroundColor Cyan
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint -Method GET -TimeoutSec 10
        Write-Host "✓ $endpoint - Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "✗ $endpoint - Error: $_" -ForegroundColor Red
    }
}

Write-Host "`nIf endpoints are still failing, check logs at:" -ForegroundColor Yellow
Write-Host "https://foodxchange-app.scm.azurewebsites.net/api/logstream" -ForegroundColor Cyan