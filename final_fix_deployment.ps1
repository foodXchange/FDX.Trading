# Final deployment fix with correct WSGI app
$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"

Write-Host "Deploying final fix..." -ForegroundColor Green

# Create deployment package with the working fix
Write-Host "Creating deployment package..." -ForegroundColor Yellow
if (Test-Path "final_fix.zip") { Remove-Item "final_fix.zip" -Force }
Compress-Archive -Path "simple_fix.py" -DestinationPath "final_fix.zip" -Force

# Deploy the fix
Write-Host "Deploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group $resourceGroup `
    --name $appName `
    --src "final_fix.zip"

# Restart the app
Write-Host "Restarting app..." -ForegroundColor Yellow
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "Waiting for startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Test the health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "https://foodxchange-app.azurewebsites.net/health/simple" -Method Get -TimeoutSec 60
    Write-Host "SUCCESS! Health endpoint response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
    
    # Test the domain too
    Write-Host "Testing fdx.trading domain..." -ForegroundColor Cyan
    $customResponse = Invoke-RestMethod -Uri "https://www.fdx.trading/health/simple" -Method Get -TimeoutSec 60 -ErrorAction SilentlyContinue
    if ($customResponse) {
        Write-Host "Custom domain also working: $($customResponse | ConvertTo-Json -Compress)" -ForegroundColor Green
    } else {
        Write-Host "Custom domain not working yet, but Azure URL is working!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error testing endpoint: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Checking current status..." -ForegroundColor Yellow
    
    try {
        $status = Invoke-WebRequest -Uri "https://foodxchange-app.azurewebsites.net/health/simple" -Method Head -TimeoutSec 30
        Write-Host "Status Code: $($status.StatusCode)" -ForegroundColor Yellow
    } catch {
        Write-Host "HTTP Status Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}