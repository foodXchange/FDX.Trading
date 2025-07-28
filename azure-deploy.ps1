# FoodXchange Azure Deployment PowerShell Script
param(
    [string]$ResourceGroup = "",
    [string]$AppName = "",
    [string]$DatabaseUrl = "",
    [string]$Location = "East US"
)

Write-Host "🚀 FoodXchange Azure Deployment" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json 2>&1 | ConvertFrom-Json
    Write-Host "✅ Azure CLI found: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI is not installed" -ForegroundColor Red
    Write-Host "Please install Azure CLI from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in to Azure
try {
    $account = az account show --output json 2>&1 | ConvertFrom-Json
    Write-Host "✅ Logged in to Azure as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure" -ForegroundColor Red
    Write-Host "Please run: az login" -ForegroundColor Yellow
    exit 1
}

# Get deployment configuration if not provided
if (-not $ResourceGroup) {
    $ResourceGroup = Read-Host "Resource group name (e.g., foodxchange-rg)"
}

if (-not $AppName) {
    $AppName = Read-Host "Web app name (e.g., foodxchange-app)"
}

if (-not $DatabaseUrl) {
    $DatabaseUrl = Read-Host "Database URL (optional, press Enter to skip)"
}

if (-not $ResourceGroup -or -not $AppName) {
    Write-Host "❌ Resource group and app name are required." -ForegroundColor Red
    exit 1
}

Write-Host "`n📝 Deployment Configuration:" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "App Name: $AppName" -ForegroundColor White
Write-Host "Location: $Location" -ForegroundColor White
if ($DatabaseUrl) {
    Write-Host "Database URL: $DatabaseUrl" -ForegroundColor White
}

$confirm = Read-Host "`nProceed with deployment? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Run the deployment script
Write-Host "`n🚀 Starting deployment..." -ForegroundColor Green
try {
    python azure_deploy.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 Deployment completed successfully!" -ForegroundColor Green
        Write-Host "🌐 Your app is available at: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ Deployment failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n❌ Error during deployment: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Set up your database connection string in Azure App Settings" -ForegroundColor White
Write-Host "2. Configure your domain and SSL certificate" -ForegroundColor White
Write-Host "3. Set up monitoring and logging" -ForegroundColor White
Write-Host "4. Configure your environment variables" -ForegroundColor White 