# Simple Azure Deployment Script
# This script deploys directly to Azure without GitHub Actions complexity

Write-Host "=== Simple Azure Deployment ===" -ForegroundColor Green
Write-Host "Direct deployment to Azure Web App" -ForegroundColor Yellow
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "Azure CLI found (version: $($azVersion.'azure-cli'))" -ForegroundColor Green
} catch {
    Write-Host "Azure CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Not logged in to Azure. Please run 'az login' first" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Deployment Configuration ===" -ForegroundColor Cyan

$resourceGroup = Read-Host "Enter your Azure resource group name (e.g., foodxchange-rg)"
$appName = Read-Host "Enter your Azure Web App name (e.g., foodxchange-app)"

Write-Host ""
Write-Host "=== Step 1: Install Dependencies ===" -ForegroundColor Cyan
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow

# Install dependencies
pip install -r requirements.txt

Write-Host "Dependencies installed!" -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 2: Deploy to Azure ===" -ForegroundColor Cyan
Write-Host "Deploying to $appName..." -ForegroundColor Yellow

# Deploy using Azure CLI
az webapp deployment source config-zip --resource-group $resourceGroup --name $appName --src .

Write-Host ""
Write-Host "=== Deployment Complete! ===" -ForegroundColor Green
Write-Host "Your app should be available at: https://$appName.azurewebsites.net" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== Optional: Restart App ===" -ForegroundColor Cyan
$restart = Read-Host "Do you want to restart the app? (y/n)"
if ($restart -eq 'y' -or $restart -eq 'Y') {
    Write-Host "Restarting app..." -ForegroundColor Yellow
    az webapp restart --name $appName --resource-group $resourceGroup
    Write-Host "App restarted!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Deployment complete! 🎉" -ForegroundColor Green 