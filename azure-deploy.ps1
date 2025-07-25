# Azure Deployment Script for FoodXchange
# Run this script after logging in with: az login

# Configuration
$RESOURCE_GROUP_NAME = "foodxchange-rg"
$LOCATION = "East US"
$APP_NAME = "foodxchange-app"
$PLAN_NAME = "foodxchange-plan"

Write-Host "🚀 Starting Azure deployment for FoodXchange..." -ForegroundColor Green

# Check if logged in
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Logged in to Azure" -ForegroundColor Green

# Create Resource Group
Write-Host "Creating resource group: $RESOURCE_GROUP_NAME" -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Create App Service Plan
Write-Host "Creating App Service Plan: $PLAN_NAME" -ForegroundColor Yellow
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP_NAME --sku B1 --is-linux

# Create Web App
Write-Host "Creating Web App: $APP_NAME" -ForegroundColor Yellow
az webapp create --resource-group $RESOURCE_GROUP_NAME --plan $PLAN_NAME --name $APP_NAME --runtime "PYTHON:3.12"

# Configure startup command
Write-Host "Configuring startup command..." -ForegroundColor Yellow
az webapp config set --resource-group $RESOURCE_GROUP_NAME --name $APP_NAME --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"

# Deploy the app
Write-Host "Deploying application..." -ForegroundColor Yellow
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP_NAME --name $APP_NAME --src app.zip

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your app is available at: https://$APP_NAME.azurewebsites.net" -ForegroundColor Cyan 