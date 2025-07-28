# Azure Deployment Emergency Fix Script
Write-Host "Azure Deployment Emergency Fix" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Configuration
$resourceGroup = "FoodXchange"
$appName = "foodxchang-2ad3c0f8"

Write-Host "`n1. Updating Azure App Service configuration..." -ForegroundColor Yellow

# Set Python version and startup command
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --linux-fx-version "PYTHON|3.12" `
    --startup-file "python startup_robust.py"

# Set application settings
az webapp config appsettings set `
    --resource-group $resourceGroup `
    --name $appName `
    --settings `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    ENABLE_ORYX_BUILD=true `
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=true `
    WEBSITE_RUN_FROM_PACKAGE=0 `
    WEBSITES_PORT=8000

Write-Host "`n2. Creating deployment package..." -ForegroundColor Yellow

# Create a minimal deployment package
$files = @(
    "requirements.txt",
    "startup_robust.py",
    "startup.txt",
    "application.py",
    "web.config",
    "app"
)

# Remove old package
if (Test-Path "emergency_deployment.zip") {
    Remove-Item "emergency_deployment.zip"
}

# Create new package
foreach ($file in $files) {
    if (Test-Path $file) {
        Compress-Archive -Path $file -Update -DestinationPath "emergency_deployment.zip"
    }
}

Write-Host "`n3. Deploying to Azure..." -ForegroundColor Yellow

# Deploy using zip deployment
az webapp deployment source config-zip `
    --resource-group $resourceGroup `
    --name $appName `
    --src "emergency_deployment.zip"

Write-Host "`n4. Restarting app service..." -ForegroundColor Yellow

# Restart the app
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "`n5. Checking deployment status..." -ForegroundColor Yellow

# Wait a bit
Start-Sleep -Seconds 10

# Check app status
$appUrl = "https://www.fdx.trading"
try {
    $response = Invoke-WebRequest -Uri "$appUrl/health" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "`nSuccess! App is responding at $appUrl" -ForegroundColor Green
    }
} catch {
    Write-Host "`nApp may still be starting. Check:" -ForegroundColor Yellow
    Write-Host "- Azure Portal > App Service > Log stream" -ForegroundColor Cyan
    Write-Host "- $appUrl (may take a few minutes)" -ForegroundColor Cyan
}

Write-Host "`nDeployment complete!" -ForegroundColor Green