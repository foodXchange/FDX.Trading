# Quick Azure Fix
Write-Host "Quick Azure Deployment Fix" -ForegroundColor Green

$resourceGroup = "FoodXchange"
$appName = "foodxchang-2ad3c0f8"

# Update startup command
Write-Host "Setting startup command..." -ForegroundColor Yellow
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --startup-file "python startup.py"

# Restart
Write-Host "Restarting app..." -ForegroundColor Yellow
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "Done! Check https://www.fdx.trading in 2-3 minutes" -ForegroundColor Green