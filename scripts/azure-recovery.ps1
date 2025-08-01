# Azure FoodXchange Recovery Script
# This script restores the last known working configuration

Write-Host "Azure FoodXchange Recovery Script" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Configuration
$resourceGroup = "foodxchange-deploy"
$webAppName = "foodxchange-deploy-app"
$workingImage = "foodxchangeacr2025deploy.azurecr.io/foodxchange:8e3c88b4e8b4b9763711f850cf917d22e786c09e"
$websitesPort = "9000"

Write-Host "`nStep 1: Checking current status..." -ForegroundColor Yellow
az webapp show --name $webAppName --resource-group $resourceGroup --query "{state:state, health:healthCheckPath}" -o table

Write-Host "`nStep 2: Setting container to last known working image..." -ForegroundColor Yellow
az webapp config container set `
  --name $webAppName `
  --resource-group $resourceGroup `
  --docker-custom-image-name $workingImage

Write-Host "`nStep 3: Setting correct port configuration..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $webAppName `
  --resource-group $resourceGroup `
  --settings WEBSITES_PORT=$websitesPort PORT=$websitesPort

Write-Host "`nStep 4: Setting production environment variables..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $webAppName `
  --resource-group $resourceGroup `
  --settings `
    ENVIRONMENT=production `
    DEBUG=False `
    DOMAIN=fdx.trading `
    BASE_URL=https://www.fdx.trading

Write-Host "`nStep 5: Restarting the web app..." -ForegroundColor Yellow
az webapp restart --name $webAppName --resource-group $resourceGroup

Write-Host "`nStep 6: Waiting for app to start (90 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

Write-Host "`nStep 7: Testing site availability..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "https://www.fdx.trading/" -UseBasicParsing -TimeoutSec 30 -Method Get -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Host "✅ Site is responding correctly!" -ForegroundColor Green
} else {
    Write-Host "❌ Site is not responding. Check logs with:" -ForegroundColor Red
    Write-Host "az webapp log tail --name $webAppName --resource-group $resourceGroup" -ForegroundColor Yellow
}

Write-Host "`nRecovery script completed." -ForegroundColor Green