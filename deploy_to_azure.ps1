# Azure Automated Deployment Script
param(
    [string]$ResourceGroup = "foodxchange-rg",
    [string]$AppName = "fdx-trading",
    [string]$Location = "East US"
)

Write-Host "Azure App Service Deployment Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Check if logged in to Azure
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}
Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green

# Check if resource group exists
Write-Host "`nChecking resource group..." -ForegroundColor Yellow
$rg = az group show --name $ResourceGroup 2>$null
if (-not $rg) {
    Write-Host "Creating resource group: $ResourceGroup" -ForegroundColor Yellow
    az group create --name $ResourceGroup --location $Location
}

# Check if app service plan exists
Write-Host "`nChecking App Service Plan..." -ForegroundColor Yellow
$planName = "$AppName-plan"
$plan = az appservice plan show --name $planName --resource-group $ResourceGroup 2>$null
if (-not $plan) {
    Write-Host "Creating App Service Plan: $planName" -ForegroundColor Yellow
    az appservice plan create `
        --name $planName `
        --resource-group $ResourceGroup `
        --sku B1 `
        --is-linux
}

# Check if web app exists
Write-Host "`nChecking Web App..." -ForegroundColor Yellow
$webapp = az webapp show --name $AppName --resource-group $ResourceGroup 2>$null
if (-not $webapp) {
    Write-Host "Creating Web App: $AppName" -ForegroundColor Yellow
    az webapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --plan $planName `
        --runtime "PYTHON:3.12"
} else {
    Write-Host "Web App already exists: $AppName" -ForegroundColor Green
}

# Configure app settings
Write-Host "`nConfiguring app settings..." -ForegroundColor Yellow
az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        SCM_DO_BUILD_DURING_DEPLOYMENT=true `
        ENABLE_ORYX_BUILD=true `
        PYTHON_ENABLE_GUNICORN_MULTIWORKERS=false `
        WEBSITES_PORT=8000 `
        WEBSITE_HEALTHCHECK_MAXPINGFAILURES=10 `
        WEBSITE_HTTPLOGGING_RETENTION_DAYS=7

# Set the startup command
Write-Host "`nSetting startup command..." -ForegroundColor Yellow
az webapp config set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --startup-file "python -m uvicorn app:app --host 0.0.0.0 --port 8000"

# Deploy the package
Write-Host "`nDeploying application..." -ForegroundColor Yellow
if (Test-Path "azure_fix_deployment.zip") {
    az webapp deploy `
        --name $AppName `
        --resource-group $ResourceGroup `
        --src-path azure_fix_deployment.zip `
        --type zip
    
    Write-Host "`nDeployment initiated!" -ForegroundColor Green
    
    # Wait for deployment
    Write-Host "Waiting for deployment to complete..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Test the deployment
    Write-Host "`nTesting deployment..." -ForegroundColor Yellow
    $appUrl = "https://$AppName.azurewebsites.net"
    
    try {
        $response = Invoke-WebRequest -Uri "$appUrl/health" -Method GET -TimeoutSec 30
        if ($response.StatusCode -eq 200) {
            Write-Host "Health check passed!" -ForegroundColor Green
            Write-Host "Response: $($response.Content)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Health check failed: $_" -ForegroundColor Red
    }
    
    Write-Host "`nApplication URL: $appUrl" -ForegroundColor Cyan
    Write-Host "Kudu Console: https://$AppName.scm.azurewebsites.net" -ForegroundColor Cyan
    Write-Host "Azure Portal: https://portal.azure.com" -ForegroundColor Cyan
    
} else {
    Write-Host "Deployment package not found. Run azure_deploy_fix.ps1 first." -ForegroundColor Red
    exit 1
}

# Show recent logs
Write-Host "`nFetching recent logs..." -ForegroundColor Yellow
az webapp log tail `
    --name $AppName `
    --resource-group $ResourceGroup `
    --provider http `
    --max-log-size 2000

Write-Host "`nDeployment complete!" -ForegroundColor Green