# Add current IP to Azure PostgreSQL firewall rules
$currentIP = "217.132.154.154"
$resourceGroup = "FoodXchangeRG"
$serverName = "foodxchangepgfr"
$ruleName = "ClientIP_$(Get-Date -Format 'yyyy-MM-dd_HHmmss')"

Write-Host "Adding firewall rule for IP: $currentIP" -ForegroundColor Green

# Login to Azure (if not already logged in)
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    az login
}

# Add firewall rule
Write-Host "Adding firewall rule..." -ForegroundColor Yellow
az postgres flexible-server firewall-rule create `
    --resource-group $resourceGroup `
    --name $serverName `
    --rule-name $ruleName `
    --start-ip-address $currentIP `
    --end-ip-address $currentIP

if ($LASTEXITCODE -eq 0) {
    Write-Host "Firewall rule added successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to add firewall rule. Please add it manually in Azure Portal." -ForegroundColor Red
}

# List all firewall rules
Write-Host "`nCurrent firewall rules:" -ForegroundColor Cyan
az postgres flexible-server firewall-rule list `
    --resource-group $resourceGroup `
    --name $serverName `
    --output table