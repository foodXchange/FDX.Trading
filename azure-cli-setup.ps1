# Azure CLI Local Setup for FoodXchange
Write-Host "🚀 Azure CLI Local Setup for FoodXchange" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if Azure CLI is installed
try {
    $azVersion = az --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Azure CLI found" -ForegroundColor Green
    } else {
        throw "Azure CLI not found"
    }
} catch {
    Write-Host "❌ Azure CLI not found. Installing..." -ForegroundColor Red
    Write-Host "Please download and install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    Write-Host "After installation, restart this script." -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit 1
}

# Check if logged in
Write-Host "Checking login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "🔐 Not logged in. Starting login process..." -ForegroundColor Yellow
    az login
} else {
    Write-Host "✅ Already logged in" -ForegroundColor Green
}

# Show current subscription
Write-Host "`n📋 Current Azure Subscription:" -ForegroundColor Cyan
az account show --query "name" -o tsv

# Show FoodXchange resources
Write-Host "`n🏗️  FoodXchange Resources:" -ForegroundColor Cyan
az resource list --resource-group foodxchange-rg --query "[].{Name:name, Type:type, Location:location}" -o table

Write-Host "`n🎯 Quick Commands:" -ForegroundColor Cyan
Write-Host "  - View resources: az resource list --resource-group foodxchange-rg" -ForegroundColor White
Write-Host "  - View app service: az webapp show --name foodxchange-app --resource-group foodxchange-rg" -ForegroundColor White
Write-Host "  - View database: az postgres flexible-server show --name foodxchangepgfr --resource-group foodxchange-rg" -ForegroundColor White
Write-Host "  - Deploy app: az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange-app --src app.zip" -ForegroundColor White

Read-Host "`nPress Enter to continue" 