# Azure HEAD Request Fix Deployment Script
param(
    [string]$ResourceGroup = "foodxchange-rg",
    [string]$AppName = "foodxchange-app"
)

Write-Host "Deploying Azure HEAD request fix for FoodXchange..." -ForegroundColor Green

# Check if we're logged in to Azure
$account = az account show 2>$null | ConvertFrom-Json
if (!$account) {
    Write-Host "Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

Write-Host "Using Azure account: $($account.user.name)" -ForegroundColor Cyan

# Stop the app first to ensure clean deployment
Write-Host "`nStopping the app service..." -ForegroundColor Yellow
az webapp stop --name $AppName --resource-group $ResourceGroup

# Create deployment package
Write-Host "`nCreating deployment package..." -ForegroundColor Yellow
$deployFiles = @(
    "app.py",
    "minimal_app.py",
    "requirements.txt",
    "startup.sh",
    "web.config",
    "runtime.txt"
)

# Remove old deployment zip if exists
if (Test-Path "azure_fix_deploy.zip") {
    Remove-Item "azure_fix_deploy.zip" -Force
}

# Create the zip file
Compress-Archive -Path $deployFiles -DestinationPath "azure_fix_deploy.zip" -Force

Write-Host "Deployment package created: azure_fix_deploy.zip" -ForegroundColor Green

# Deploy to Azure
Write-Host "`nDeploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip --resource-group $ResourceGroup --name $AppName --src azure_fix_deploy.zip

# Start the app
Write-Host "`nStarting the app service..." -ForegroundColor Yellow
az webapp start --name $AppName --resource-group $ResourceGroup

# Wait for deployment to complete
Write-Host "`nWaiting for deployment to complete (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test the health endpoint
Write-Host "`nTesting health endpoints..." -ForegroundColor Yellow

# Test GET request
Write-Host "`nTesting GET /health:" -ForegroundColor Cyan
try {
    $healthResponse = Invoke-WebRequest -Uri "https://$AppName.azurewebsites.net/health" -Method GET -TimeoutSec 10
    Write-Host "Status: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($healthResponse.Content)" -ForegroundColor Green
} catch {
    Write-Host "GET /health failed: $_" -ForegroundColor Red
}

# Test HEAD request
Write-Host "`nTesting HEAD /health:" -ForegroundColor Cyan
try {
    $headResponse = Invoke-WebRequest -Uri "https://$AppName.azurewebsites.net/health" -Method HEAD -TimeoutSec 10
    Write-Host "Status: $($headResponse.StatusCode)" -ForegroundColor Green
    Write-Host "HEAD request successful!" -ForegroundColor Green
} catch {
    Write-Host "HEAD /health failed: $_" -ForegroundColor Red
}

# Check recent logs
Write-Host "`nChecking recent application logs..." -ForegroundColor Yellow
az webapp log tail --name $AppName --resource-group $ResourceGroup --timeout 20

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Your app should now be accessible at: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Domain: https://www.fdx.trading" -ForegroundColor Cyan