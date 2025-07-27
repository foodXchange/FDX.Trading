# Quick Azure App Restart Script
Write-Host "Restarting Azure App Service..." -ForegroundColor Cyan

# Check Azure CLI login
$loginCheck = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Azure CLI first: az login" -ForegroundColor Red
    exit 1
}

# Restart the app
Write-Host "Stopping app..." -ForegroundColor Yellow
az webapp stop --name foodxchange-app --resource-group foodxchange-rg

Start-Sleep -Seconds 5

Write-Host "Starting app..." -ForegroundColor Yellow
az webapp start --name foodxchange-app --resource-group foodxchange-rg

Write-Host "App restarted successfully!" -ForegroundColor Green
Write-Host "Wait 2-3 minutes for the app to fully initialize." -ForegroundColor Yellow