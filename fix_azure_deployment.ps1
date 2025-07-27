# Fix Azure Deployment Script
# This script fixes the startup configuration and restarts the Azure App Service

Write-Host "=== Fixing Azure Deployment for fdx-trading.com ===" -ForegroundColor Cyan

# Check if Azure CLI is logged in
Write-Host "`n1. Checking Azure CLI login status..." -ForegroundColor Yellow
$loginStatus = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure CLI. Please run: az login" -ForegroundColor Red
    exit 1
}

Write-Host "Logged in to Azure CLI" -ForegroundColor Green

# Set variables
$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"

# Check app status
Write-Host "`n2. Checking current app status..." -ForegroundColor Yellow
$appStatus = az webapp show --name $appName --resource-group $resourceGroup --query "state" -o tsv 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "App Status: $appStatus" -ForegroundColor Green
} else {
    Write-Host "Could not retrieve app status" -ForegroundColor Red
}

# Stop the app first
Write-Host "`n3. Stopping the app service..." -ForegroundColor Yellow
az webapp stop --name $appName --resource-group $resourceGroup
Start-Sleep -Seconds 5

# Start the app
Write-Host "`n4. Starting the app service..." -ForegroundColor Yellow
az webapp start --name $appName --resource-group $resourceGroup
Start-Sleep -Seconds 10

# Check deployment status
Write-Host "`n5. Checking deployment logs..." -ForegroundColor Yellow
$deploymentLogs = az webapp log deployment show --name $appName --resource-group $resourceGroup --output json | ConvertFrom-Json
if ($deploymentLogs) {
    Write-Host "Last deployment: $($deploymentLogs.received_time)" -ForegroundColor Green
    Write-Host "Status: $($deploymentLogs.status)" -ForegroundColor Green
}

# Test the endpoints
Write-Host "`n6. Testing endpoints..." -ForegroundColor Yellow

# Test Azure URL
Write-Host "`nTesting Azure URL..." -ForegroundColor Cyan
try {
    $azureResponse = Invoke-WebRequest -Uri "https://$appName.azurewebsites.net/health" -Method Get -TimeoutSec 30 -UseBasicParsing
    if ($azureResponse.StatusCode -eq 200) {
        Write-Host "✓ Azure URL is working: https://$appName.azurewebsites.net" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Azure URL is not responding properly" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

# Show app logs
Write-Host "`n7. Recent application logs:" -ForegroundColor Yellow
az webapp log tail --name $appName --resource-group $resourceGroup --timeout 30

Write-Host "`n=== Azure Deployment Fix Complete ===" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Configure DNS in Namecheap (see instructions below)" -ForegroundColor White
Write-Host "2. Wait 15-60 minutes for DNS propagation" -ForegroundColor White
Write-Host "3. Test https://fdx-trading.com" -ForegroundColor White

Write-Host "`n=== DNS Configuration Instructions ===" -ForegroundColor Cyan
$dnsInstructions = @"
1. Login to Namecheap.com
2. Go to Domain List -> fdx-trading.com -> Manage
3. Click 'Advanced DNS' tab
4. Add these records:

   Type: CNAME
   Host: @
   Value: $appName.azurewebsites.net
   TTL: Automatic

   Type: CNAME
   Host: www
   Value: $appName.azurewebsites.net
   TTL: Automatic

5. Save changes and wait for DNS propagation
"@
Write-Host $dnsInstructions -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")