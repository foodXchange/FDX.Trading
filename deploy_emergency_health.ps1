# Emergency deployment to fix health endpoints
Write-Host "Emergency deployment to fix Azure health endpoints..." -ForegroundColor Red

# Create deployment files
Write-Host "Creating emergency deployment files..." -ForegroundColor Yellow

# Copy emergency script as main application
Copy-Item "emergency_health_fix.py" "application.py" -Force

# Create minimal requirements.txt
@'
Flask==3.0.0
'@ | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Create startup command
"python application.py" | Out-File -FilePath "startup.txt" -Encoding UTF8

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Cyan
$files = @("application.py", "requirements.txt", "startup.txt")

if (Test-Path "emergency_health.zip") { Remove-Item "emergency_health.zip" -Force }
Compress-Archive -Path $files -DestinationPath "emergency_health.zip" -Force

# Deploy to Azure
Write-Host "Deploying to Azure..." -ForegroundColor Green
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path emergency_health.zip --type zip

# Configure startup
Write-Host "Configuring startup..." -ForegroundColor Cyan
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "python application.py"

# Ensure Python packages are installed
az webapp config appsettings set --resource-group foodxchange-rg --name foodxchange-app --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Restart app
Write-Host "Restarting app..." -ForegroundColor Cyan
az webapp restart --resource-group foodxchange-rg --name foodxchange-app

Write-Host "`nEmergency deployment complete!" -ForegroundColor Green
Write-Host "Check in 30 seconds:" -ForegroundColor Yellow
Write-Host "- https://www.fdx.trading/health/simple" -ForegroundColor Cyan
Write-Host "- https://foodxchange-app.azurewebsites.net/health/simple" -ForegroundColor Cyan

# Clean up temporary files
Remove-Item "application.py" -Force -ErrorAction SilentlyContinue