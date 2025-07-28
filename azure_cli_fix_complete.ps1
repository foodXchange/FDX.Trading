# Complete Azure CLI Fix Script for FoodXchange 503 Error
Write-Host "Starting complete Azure fix process..." -ForegroundColor Green

$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"

# Step 1: Stop the app
Write-Host "`nStep 1: Stopping web app..." -ForegroundColor Yellow
az webapp stop --resource-group $resourceGroup --name $appName

# Step 2: Clear problematic settings
Write-Host "`nStep 2: Clearing app settings..." -ForegroundColor Yellow
az webapp config appsettings delete --resource-group $resourceGroup --name $appName --setting-names WEBSITE_RUN_FROM_PACKAGE WEBSITE_RUN_FROM_ZIP 2>$null

# Step 3: Set proper Python version
Write-Host "`nStep 3: Setting Python version..." -ForegroundColor Yellow
az webapp config set --resource-group $resourceGroup --name $appName --linux-fx-version "PYTHON|3.11"

# Step 4: Enable build
Write-Host "`nStep 4: Enabling build settings..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $resourceGroup --name $appName --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true

# Step 5: Set startup command
Write-Host "`nStep 5: Setting startup command..." -ForegroundColor Yellow
az webapp config set --resource-group $resourceGroup --name $appName --startup-file "gunicorn --bind 0.0.0.0:8000 --timeout 600 --workers 1 app:app"

# Step 6: Start the app
Write-Host "`nStep 6: Starting web app..." -ForegroundColor Yellow
az webapp start --resource-group $resourceGroup --name $appName

# Step 7: Wait for startup
Write-Host "`nStep 7: Waiting for app to start (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Step 8: Test health endpoint
Write-Host "`nStep 8: Testing health endpoint..." -ForegroundColor Yellow
$healthUrl = "https://www.fdx.trading/health"
try {
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Health endpoint is working!" -ForegroundColor Green
        Write-Host $response.Content
    } else {
        Write-Host "❌ Health endpoint returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Health endpoint failed: $_" -ForegroundColor Red
    
    # Try direct Azure URL
    Write-Host "`nTrying direct Azure URL..." -ForegroundColor Yellow
    $azureUrl = "https://foodxchange-app.azurewebsites.net/health"
    try {
        $azureResponse = Invoke-WebRequest -Uri $azureUrl -UseBasicParsing -TimeoutSec 30
        Write-Host "Azure URL response: $($azureResponse.StatusCode)" -ForegroundColor Cyan
    } catch {
        Write-Host "Azure URL also failed" -ForegroundColor Red
    }
}

Write-Host "`nFix process completed. If still not working, check:" -ForegroundColor Cyan
Write-Host "1. https://foodxchange-app.scm.azurewebsites.net for Kudu console"
Write-Host "2. az webapp log tail --resource-group $resourceGroup --name $appName"
Write-Host "3. Consider scaling up to S1 temporarily"