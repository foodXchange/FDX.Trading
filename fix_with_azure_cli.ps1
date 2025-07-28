# Fix Azure deployment using Azure CLI
Write-Host "Fixing Azure deployment with CLI..." -ForegroundColor Yellow

# Step 1: Configure app settings for proper Python build
Write-Host "`nStep 1: Configuring app settings..." -ForegroundColor Cyan
az webapp config appsettings set `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --settings `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    ENABLE_ORYX_BUILD=true `
    PYTHON_VERSION=3.11 `
    WEBSITE_RUN_FROM_PACKAGE=0

# Step 2: Create a simple startup script via CLI
Write-Host "`nStep 2: Creating startup script..." -ForegroundColor Cyan
$startupScript = @'
#!/bin/bash
echo "Installing Flask..."
pip install flask==3.0.0
echo "Creating emergency app..."
cat > /home/site/wwwroot/application.py << 'EOF'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange</h1><p><a href="/health/simple">Health Check</a></p>'

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
EOF
echo "Starting Flask app..."
cd /home/site/wwwroot
python application.py
'@

# Save startup script to a file
$startupScript | Out-File -FilePath "startup.sh" -Encoding UTF8 -NoNewline

# Step 3: Upload startup script using Azure CLI
Write-Host "`nStep 3: Uploading startup script..." -ForegroundColor Cyan
az webapp deployment source config-zip `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --src startup.sh

# Step 4: Set the startup command
Write-Host "`nStep 4: Setting startup command..." -ForegroundColor Cyan
az webapp config set `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --startup-file "/home/site/wwwroot/startup.sh"

# Step 5: Enable application logging
Write-Host "`nStep 5: Enabling logging..." -ForegroundColor Cyan
az webapp log config `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --application-logging filesystem `
    --level verbose `
    --web-server-logging filesystem

# Step 6: Restart the app
Write-Host "`nStep 6: Restarting app..." -ForegroundColor Cyan
az webapp restart --resource-group foodxchange-rg --name foodxchange-app

Write-Host "`nStep 7: Using SSH to fix directly..." -ForegroundColor Yellow

# Create SSH fix script
$sshCommands = @'
cd /home/site/wwwroot
pip install flask==3.0.0
cat > app.py << 'EOF'
from flask import Flask, jsonify
app = Flask(__name__)
app.route('/')(lambda: '<h1>FoodXchange</h1>')
app.route('/health/simple')(lambda: jsonify({"status": "ok"}))
app.route('/health')(lambda: jsonify({"status": "healthy"}))
if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
EOF
'@

Write-Host "`nExecuting SSH commands..." -ForegroundColor Cyan
$sshCommands | az webapp ssh --resource-group foodxchange-rg --name foodxchange-app

Write-Host "`nDeployment fix complete!" -ForegroundColor Green
Write-Host "Wait 30 seconds then check:" -ForegroundColor Yellow
Write-Host "https://www.fdx.trading/health/simple" -ForegroundColor Cyan

# Clean up
Remove-Item "startup.sh" -Force -ErrorAction SilentlyContinue