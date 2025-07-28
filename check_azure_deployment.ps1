# Azure Deployment Health Check Script
param(
    [string]$ResourceGroup = "foodxchange-rg",
    [string]$AppName = "foodxchange-app"
)

Write-Host "Checking Azure Web App deployment status..." -ForegroundColor Green

# Check app status
Write-Host "`nApp Status:" -ForegroundColor Yellow
az webapp show --name $AppName --resource-group $ResourceGroup --query state -o tsv

# Get recent logs
Write-Host "`nRecent Deployment Logs:" -ForegroundColor Yellow
az webapp log deployment show --name $AppName --resource-group $ResourceGroup

# Test health endpoint
Write-Host "`nTesting Health Endpoint:" -ForegroundColor Yellow
$healthUrl = "https://$AppName.azurewebsites.net/health"
try {
    $response = Invoke-WebRequest -Uri $healthUrl -Method GET -TimeoutSec 10
    Write-Host "Health Check Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Health Check Failed: $_" -ForegroundColor Red
}

# Get app settings
Write-Host "`nCurrent App Settings:" -ForegroundColor Yellow
az webapp config appsettings list --name $AppName --resource-group $ResourceGroup --query "[?name=='SCM_DO_BUILD_DURING_DEPLOYMENT' || name=='WEBSITE_RUN_FROM_PACKAGE' || name=='WEBSITES_PORT'].{name:name, value:value}" -o table

# Get startup command
Write-Host "`nStartup Command:" -ForegroundColor Yellow
az webapp config show --name $AppName --resource-group $ResourceGroup --query "linuxFxVersion" -o tsv

Write-Host "`nDeployment check complete!" -ForegroundColor Green