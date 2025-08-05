# PowerShell script to open Netdata ports in Azure NSG
# Requires Azure CLI to be installed and logged in

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Opening Netdata Ports in Azure NSG" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Variables
$resourceGroup = "fdx-resources"
$nsgName = "fdx-vm-nsg"
$vmName = "fdx-vm"

# Check if logged in to Azure
Write-Host "`nChecking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}

Write-Host "Logged in to Azure" -ForegroundColor Green

# Get current NSG rules
Write-Host "`nCurrent NSG rules:" -ForegroundColor Yellow
az network nsg rule list --resource-group $resourceGroup --nsg-name $nsgName --output table

# Open port 3000 for Netdata Web UI
Write-Host "`nOpening port 3000 for Netdata Web UI..." -ForegroundColor Yellow
az network nsg rule create `
    --resource-group $resourceGroup `
    --nsg-name $nsgName `
    --name "Allow-Netdata-3000" `
    --priority 1030 `
    --direction Inbound `
    --access Allow `
    --protocol Tcp `
    --source-address-prefixes "*" `
    --source-port-ranges "*" `
    --destination-address-prefixes "*" `
    --destination-port-ranges 3000 `
    --description "Allow Netdata monitoring on port 3000"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Port 3000 opened successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to open port 3000" -ForegroundColor Red
}

# Open port 19999 for Netdata API
Write-Host "`nOpening port 19999 for Netdata API..." -ForegroundColor Yellow
az network nsg rule create `
    --resource-group $resourceGroup `
    --nsg-name $nsgName `
    --name "Allow-Netdata-19999" `
    --priority 1031 `
    --direction Inbound `
    --access Allow `
    --protocol Tcp `
    --source-address-prefixes "*" `
    --source-port-ranges "*" `
    --destination-address-prefixes "*" `
    --destination-port-ranges 19999 `
    --description "Allow Netdata API on port 19999"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Port 19999 opened successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to open port 19999" -ForegroundColor Red
}

# Show updated NSG rules
Write-Host "`nUpdated NSG rules:" -ForegroundColor Yellow
az network nsg rule list --resource-group $resourceGroup --nsg-name $nsgName --output table

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Port Configuration Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "`nNetdata should now be accessible at:" -ForegroundColor Green
Write-Host "  • http://4.206.1.15:3000  (Web UI)" -ForegroundColor White
Write-Host "  • http://4.206.1.15:19999 (API)" -ForegroundColor White
Write-Host "`nNote: It may take a minute for Azure to apply the changes." -ForegroundColor Yellow