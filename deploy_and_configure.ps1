# Azure Deployment and Configuration Script
# This script deploys FoodXchange app and configures Azure OpenAI

Write-Host "=== FoodXchange Azure Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"
$planName = "foodxchange-plan"
$location = "East US"

# Check if logged in to Azure
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure. Logging in..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Azure login failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Logged in to Azure successfully." -ForegroundColor Green
Write-Host ""

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $resourceGroup --location "$location" --output none
if ($LASTEXITCODE -eq 0) {
    Write-Host "Resource group created/updated." -ForegroundColor Green
}

# Create App Service Plan
Write-Host "Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create --name $planName --resource-group $resourceGroup --sku B1 --is-linux --output none
if ($LASTEXITCODE -eq 0) {
    Write-Host "App Service Plan created/updated." -ForegroundColor Green
}

# Create Web App
Write-Host "Creating Web App..." -ForegroundColor Yellow
az webapp create --resource-group $resourceGroup --plan $planName --name $appName --runtime "PYTHON:3.12" --output none
if ($LASTEXITCODE -eq 0) {
    Write-Host "Web App created/updated." -ForegroundColor Green
}

# Configure startup command
Write-Host "Configuring startup command..." -ForegroundColor Yellow
$startupCommand = "gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app"
az webapp config set --resource-group $resourceGroup --name $appName --startup-file "$startupCommand" --output none
if ($LASTEXITCODE -eq 0) {
    Write-Host "Startup command configured." -ForegroundColor Green
}

# Set environment variables for Azure OpenAI
Write-Host "Configuring Azure OpenAI settings..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $resourceGroup --name $appName --settings `
    AZURE_OPENAI_ENDPOINT="https://your-openai-resource.openai.azure.com/" `
    AZURE_OPENAI_API_KEY="your-api-key" `
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o" `
    AZURE_OPENAI_API_VERSION="2024-02-15-preview" `
    --output none

Write-Host "Please update the Azure OpenAI settings with your actual values!" -ForegroundColor Yellow

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Yellow
python create_deployment_package.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment package created." -ForegroundColor Green
}

# Deploy the app
Write-Host "Deploying application..." -ForegroundColor Yellow
az webapp deployment source config-zip --resource-group $resourceGroup --name $appName --src foodxchange_deployment.zip --output none
if ($LASTEXITCODE -eq 0) {
    Write-Host "Application deployed successfully!" -ForegroundColor Green
}

# Get the app URL
$hostname = az webapp show --resource-group $resourceGroup --name $appName --query defaultHostName -o tsv
$appUrl = "https://$hostname"

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Green
Write-Host "App URL: $appUrl" -ForegroundColor Cyan
Write-Host "Health Check: $appUrl/health" -ForegroundColor Cyan
Write-Host "System Status: $appUrl/system-status" -ForegroundColor Cyan
Write-Host ""

# Option to get publish profile
$getProfile = Read-Host "Do you want to get the publish profile for GitHub Actions? (y/n)"
if ($getProfile -eq 'y') {
    Write-Host "Getting publish profile..." -ForegroundColor Yellow
    $profilePath = "publish_profile.xml"
    az webapp deployment list-publishing-profiles --name $appName --resource-group $resourceGroup --xml > $profilePath
    Write-Host "Publish profile saved to: $profilePath" -ForegroundColor Green
    Write-Host ""
    Write-Host "To use with GitHub Actions:" -ForegroundColor Yellow
    Write-Host "1. Copy the contents of $profilePath" -ForegroundColor White
    Write-Host "2. Go to your GitHub repository -> Settings -> Secrets" -ForegroundColor White
    Write-Host "3. Add a new secret named: AZUREAPPSERVICE_PUBLISHPROFILE" -ForegroundColor White
    Write-Host "4. Paste the XML content as the secret value" -ForegroundColor White
}

Write-Host ""
Write-Host "Deployment script completed!" -ForegroundColor Green