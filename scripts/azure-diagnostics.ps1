# Azure FoodXchange Diagnostics Script
# This script checks the current health and configuration

Write-Host "Azure FoodXchange Diagnostics" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

$resourceGroup = "foodxchange-deploy"
$webAppName = "foodxchange-deploy-app"

Write-Host "`n1. Web App Status:" -ForegroundColor Yellow
az webapp show --name $webAppName --resource-group $resourceGroup --query "{State:state, AvailabilityState:availabilityState, UsageState:usageState}" -o table

Write-Host "`n2. Container Configuration:" -ForegroundColor Yellow
az webapp show --name $webAppName --resource-group $resourceGroup --query "siteConfig.linuxFxVersion" -o tsv

Write-Host "`n3. Port Configuration:" -ForegroundColor Yellow
az webapp config appsettings list --name $webAppName --resource-group $resourceGroup --query "[?name=='WEBSITES_PORT' || name=='PORT'].{Name:name, Value:value}" -o table

Write-Host "`n4. Custom Domains:" -ForegroundColor Yellow
az webapp config hostname list --webapp-name $webAppName --resource-group $resourceGroup --query "[].{Hostname:name, SSL:sslState}" -o table

Write-Host "`n5. Site Availability Test:" -ForegroundColor Yellow
$urls = @("https://www.fdx.trading/", "https://fdx.trading/", "https://foodxchange-deploy-app.azurewebsites.net/")
foreach ($url in $urls) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10 -Method Head -ErrorAction Stop
        Write-Host "✅ $url - Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $url - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n6. Container Registry Settings:" -ForegroundColor Yellow
az webapp config container show --name $webAppName --resource-group $resourceGroup --query "[?name=='DOCKER_REGISTRY_SERVER_URL'].value" -o tsv

Write-Host "`n7. Recent Activity Log (Errors/Warnings):" -ForegroundColor Yellow
$endTime = Get-Date
$startTime = $endTime.AddHours(-1)
az monitor activity-log list `
  --resource-group $resourceGroup `
  --start-time $startTime.ToString("yyyy-MM-ddTHH:mm:ssZ") `
  --query "[?level=='Error' || level=='Warning'].{Time:eventTimestamp, Level:level, Status:status.value}" `
  --output table

Write-Host "`nDiagnostics completed." -ForegroundColor Cyan
Write-Host "To view live logs, run:" -ForegroundColor Yellow
Write-Host "az webapp log tail --name $webAppName --resource-group $resourceGroup" -ForegroundColor White