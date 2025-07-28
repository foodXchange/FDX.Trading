# Create fresh deployment
Write-Host "Creating fresh deployment directory..." -ForegroundColor Yellow

# Create temporary directory
$tempDir = "temp_deploy"
if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Change to temp directory
Push-Location $tempDir

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

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        "status": "healthy",
        "service": "foodxchange",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
'@ | Out-File -FilePath "app.py" -Encoding UTF8

# Create requirements.txt
"Flask==3.0.0" | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Deploy using az webapp up
Write-Host "`nDeploying to Azure..." -ForegroundColor Green
az webapp up --resource-group foodxchange-rg --name foodxchange-app --runtime "PYTHON:3.11"

# Return to original directory
Pop-Location

# Clean up
Remove-Item $tempDir -Recurse -Force

Write-Host "`nDeployment complete!" -ForegroundColor Green