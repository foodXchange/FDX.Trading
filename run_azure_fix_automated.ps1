# Automated Azure fix script (non-interactive)
$ErrorActionPreference = "Continue"

Write-Host "Starting automated Azure 503 fix..." -ForegroundColor Green

# Variables
$ResourceGroup = "foodxchange-rg"
$AppName = "foodxchange-app"

# Stop the app service
Write-Host "`nStopping App Service..." -ForegroundColor Yellow
az webapp stop --name $AppName --resource-group $ResourceGroup 2>$null

# Create deployment
Write-Host "`nCreating deployment package..." -ForegroundColor Yellow

# Use the startup_fixed.py if it exists
if (Test-Path "startup_fixed.py") {
    Copy-Item "startup_fixed.py" "startup.py" -Force
    Write-Host "Using startup_fixed.py"
}

# Deploy
Write-Host "`nDeploying to Azure..." -ForegroundColor Yellow
az webapp deploy --resource-group $ResourceGroup --name $AppName --src-path . --type zip 2>&1 | Out-Host

# Start the app
Write-Host "`nStarting App Service..." -ForegroundColor Yellow
az webapp start --name $AppName --resource-group $ResourceGroup 2>$null

Write-Host "`nWaiting 60 seconds for app to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Test endpoints
Write-Host "`nTesting endpoints..." -ForegroundColor Yellow

$endpoints = @(
    "https://foodxchange-app.azurewebsites.net/",
    "https://foodxchange-app.azurewebsites.net/health",
    "https://www.fdx.trading/",
    "https://www.fdx.trading/health"
)

foreach ($url in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        Write-Host "✓ $url - Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "✗ $url - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nFix complete!" -ForegroundColor Green