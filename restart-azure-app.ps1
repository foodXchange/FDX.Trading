# Restart Azure App Service
Write-Host "Restarting FoodXchange Azure App Service..." -ForegroundColor Cyan

# Login to Azure (if not already logged in)
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    az login
}

# Restart the web app
Write-Host "`nRestarting foodxchange-app..." -ForegroundColor Green
az webapp restart --name foodxchange-app --resource-group foodxchange-rg

# Check status
Write-Host "`nChecking app status..." -ForegroundColor Green
$state = az webapp show --name foodxchange-app --resource-group foodxchange-rg --query state -o tsv
Write-Host "App State: $state" -ForegroundColor $(if($state -eq "Running"){"Green"}else{"Red"})

# Show app URL
Write-Host "`nApp URLs:" -ForegroundColor Cyan
Write-Host "Azure URL: https://foodxchange-app.azurewebsites.net" -ForegroundColor White
Write-Host "Custom Domain: https://fdx.trading (pending DNS setup)" -ForegroundColor White
Write-Host "WWW Domain: https://www.fdx-trading.com (pending DNS setup)" -ForegroundColor White

# Tail logs
Write-Host "`nShowing recent logs (press Ctrl+C to stop)..." -ForegroundColor Yellow
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg