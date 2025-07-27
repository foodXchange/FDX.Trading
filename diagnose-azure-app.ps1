# Diagnose Azure App Service Issues
Write-Host "=== Diagnosing FoodXchange Azure App ===" -ForegroundColor Cyan

# Check if Azure CLI is logged in
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Please login to Azure first..." -ForegroundColor Yellow
    az login
}

$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"

Write-Host "`n1. Checking App Service Status..." -ForegroundColor Yellow
$appStatus = az webapp show --name $appName --resource-group $resourceGroup --query "state" -o tsv
$appHealth = az webapp show --name $appName --resource-group $resourceGroup --query "healthCheckPath" -o tsv
Write-Host "   App State: $appStatus" -ForegroundColor $(if($appStatus -eq "Running"){"Green"}else{"Red"})
Write-Host "   Health Check Path: $(if($appHealth){"$appHealth"}else{"Not configured"})" -ForegroundColor Gray

Write-Host "`n2. Checking Recent Logs..." -ForegroundColor Yellow
Write-Host "   Fetching last 50 log entries..." -ForegroundColor Gray
$logs = az webapp log tail --name $appName --resource-group $resourceGroup --lines 50 2>&1 | Out-String
if ($logs -like "*error*" -or $logs -like "*failed*") {
    Write-Host "   [ERROR] Found errors in logs!" -ForegroundColor Red
    $logs -split "`n" | Where-Object { $_ -like "*error*" -or $_ -like "*failed*" } | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Red
    }
} else {
    Write-Host "   No obvious errors found in recent logs" -ForegroundColor Green
}

Write-Host "`n3. Checking App Settings..." -ForegroundColor Yellow
$settings = az webapp config appsettings list --name $appName --resource-group $resourceGroup | ConvertFrom-Json
$requiredSettings = @("AZURE_STORAGE_CONNECTION_STRING", "DATABASE_URL", "AZURE_OPENAI_API_KEY")
foreach ($setting in $requiredSettings) {
    $found = $settings | Where-Object { $_.name -eq $setting }
    if ($found) {
        Write-Host "   [OK] $setting is configured" -ForegroundColor Green
    } else {
        Write-Host "   [MISSING] $setting not found!" -ForegroundColor Red
    }
}

Write-Host "`n4. Checking Deployment Status..." -ForegroundColor Yellow
$deployment = az webapp deployment list --name $appName --resource-group $resourceGroup | ConvertFrom-Json | Select-Object -First 1
if ($deployment) {
    Write-Host "   Last Deployment: $($deployment.end_time)" -ForegroundColor Gray
    Write-Host "   Status: $($deployment.status)" -ForegroundColor $(if($deployment.status -eq 4){"Green"}else{"Red"})
}

Write-Host "`n5. Quick Fixes to Try:" -ForegroundColor Cyan
Write-Host "   a) Restart the app:" -ForegroundColor White
Write-Host "      az webapp restart --name $appName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host "`n   b) Check live logs:" -ForegroundColor White
Write-Host "      az webapp log tail --name $appName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host "`n   c) SSH into the container:" -ForegroundColor White
Write-Host "      az webapp ssh --name $appName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host "`n   d) View deployment logs:" -ForegroundColor White
Write-Host "      https://$appName.scm.azurewebsites.net/api/deployments" -ForegroundColor Gray

$restart = Read-Host "`nWould you like to restart the app now? (y/n)"
if ($restart -eq 'y') {
    Write-Host "`nRestarting app..." -ForegroundColor Green
    az webapp restart --name $appName --resource-group $resourceGroup
    Write-Host "App restarted. Wait 30-60 seconds and check again." -ForegroundColor Yellow
}