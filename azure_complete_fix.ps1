# Complete Azure Deployment Fix Script
# This script diagnoses and fixes the HEAD request issue causing "Application Error"

param(
    [string]$ResourceGroup = "foodxchange-rg",
    [string]$AppName = "foodxchange-app"
)

Write-Host @"

=====================================
Azure App Service Fix Script
=====================================
App Name: $AppName
Resource Group: $ResourceGroup
Domain: https://www.fdx.trading
=====================================

"@ -ForegroundColor Cyan

# Function to check Azure login
function Test-AzureLogin {
    $account = az account show 2>$null | ConvertFrom-Json
    if (!$account) {
        Write-Host "ERROR: Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
        return $false
    }
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
    return $true
}

# Check login
if (!(Test-AzureLogin)) {
    exit 1
}

# Step 1: Diagnose the current issue
Write-Host "`n[STEP 1] Diagnosing current deployment status..." -ForegroundColor Yellow

# Get app status
$appStatus = az webapp show --name $AppName --resource-group $ResourceGroup --query state -o tsv
Write-Host "App Status: $appStatus"

# Get current deployment info
Write-Host "`nCurrent deployment configuration:"
az webapp config show --name $AppName --resource-group $ResourceGroup --query "{startupCommand:startupCommand, linuxFxVersion:linuxFxVersion, pythonVersion:pythonVersion}" -o table

# Step 2: Create the fixed deployment package
Write-Host "`n[STEP 2] Creating fixed deployment package..." -ForegroundColor Yellow

# Create a minimal requirements.txt with exact versions
$requirements = @"
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
"@
$requirements | Out-File -FilePath "requirements.txt" -Encoding UTF8

Write-Host "Requirements.txt updated with minimal dependencies"

# Ensure startup.sh has proper line endings
$startupContent = @"
#!/bin/bash
echo "Starting FoodXchange API with HEAD request support..."
python -m uvicorn minimal_app:app --host 0.0.0.0 --port `$PORT
"@
$startupContent | Out-File -FilePath "startup.sh" -Encoding UTF8

Write-Host "Startup.sh updated"

# Create deployment zip
$deployFiles = @(
    "app.py",
    "minimal_app.py",
    "requirements.txt",
    "startup.sh",
    "runtime.txt"
)

if (Test-Path "azure_complete_fix.zip") {
    Remove-Item "azure_complete_fix.zip" -Force
}

Compress-Archive -Path $deployFiles -DestinationPath "azure_complete_fix.zip" -Force
Write-Host "Deployment package created: azure_complete_fix.zip" -ForegroundColor Green

# Step 3: Configure Azure App Service
Write-Host "`n[STEP 3] Configuring Azure App Service..." -ForegroundColor Yellow

# Set startup command
az webapp config set --resource-group $ResourceGroup --name $AppName --startup-file "startup.sh"

# Configure app settings
$appSettings = @(
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true",
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7",
    "WEBSITES_PORT=8000",
    "PYTHON_VERSION=3.12"
)

foreach ($setting in $appSettings) {
    $parts = $setting.Split('=')
    az webapp config appsettings set --resource-group $ResourceGroup --name $AppName --settings "$setting" --output none
    Write-Host "Set: $($parts[0]) = $($parts[1])"
}

# Step 4: Deploy the fix
Write-Host "`n[STEP 4] Deploying the fix..." -ForegroundColor Yellow

# Stop the app for clean deployment
Write-Host "Stopping app service..."
az webapp stop --name $AppName --resource-group $ResourceGroup

# Deploy
Write-Host "Deploying fixed application..."
az webapp deployment source config-zip --resource-group $ResourceGroup --name $AppName --src azure_complete_fix.zip

# Start the app
Write-Host "Starting app service..."
az webapp start --name $AppName --resource-group $ResourceGroup

# Step 5: Wait and verify
Write-Host "`n[STEP 5] Waiting for deployment to complete (45 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Step 6: Comprehensive testing
Write-Host "`n[STEP 6] Testing all endpoints..." -ForegroundColor Yellow

$endpoints = @(
    @{Path="/"; Method="GET"},
    @{Path="/"; Method="HEAD"},
    @{Path="/health"; Method="GET"},
    @{Path="/health"; Method="HEAD"},
    @{Path="/health/simple"; Method="HEAD"},
    @{Path="/health/detailed"; Method="HEAD"},
    @{Path="/health/advanced"; Method="HEAD"}
)

$baseUrl = "https://$AppName.azurewebsites.net"
$allPassed = $true

foreach ($endpoint in $endpoints) {
    Write-Host "`nTesting $($endpoint.Method) $($endpoint.Path):" -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl$($endpoint.Path)" -Method $endpoint.Method -TimeoutSec 10
        Write-Host " SUCCESS (Status: $($response.StatusCode))" -ForegroundColor Green
        if ($endpoint.Method -eq "GET" -and $endpoint.Path -eq "/health") {
            Write-Host "Response: $($response.Content)" -ForegroundColor Gray
        }
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        $allPassed = $false
    }
}

# Test custom domain
Write-Host "`n[STEP 7] Testing custom domain..." -ForegroundColor Yellow
try {
    $customResponse = Invoke-WebRequest -Uri "https://www.fdx.trading/health" -Method GET -TimeoutSec 10
    Write-Host "Custom domain test: SUCCESS" -ForegroundColor Green
    Write-Host "Response: $($customResponse.Content)" -ForegroundColor Gray
} catch {
    Write-Host "Custom domain test: FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

# Get recent logs
Write-Host "`n[STEP 8] Recent application logs:" -ForegroundColor Yellow
az webapp log tail --name $AppName --resource-group $ResourceGroup --timeout 15

# Final summary
Write-Host "`n=======================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Your application is now running correctly." -ForegroundColor Green
} else {
    Write-Host "DEPLOYMENT COMPLETED WITH ISSUES" -ForegroundColor Yellow
    Write-Host "Some endpoints failed testing. Check the logs above." -ForegroundColor Yellow
}
Write-Host "=======================================" -ForegroundColor Cyan

Write-Host "`nAccess your application at:" -ForegroundColor Cyan
Write-Host "- Azure URL: https://$AppName.azurewebsites.net" -ForegroundColor White
Write-Host "- Custom Domain: https://www.fdx.trading" -ForegroundColor White

Write-Host "`nUseful commands:" -ForegroundColor Yellow
Write-Host "- View logs: az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
Write-Host "- SSH into app: az webapp ssh --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
Write-Host "- View deployment logs: az webapp log deployment show --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray