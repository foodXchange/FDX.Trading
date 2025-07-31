# Azure Infrastructure Cleanup Script
# This script will help you clean up Azure resources safely

param(
    [string]$ResourceGroupName = "foodxchange-rg",
    [string]$Domain = "fdx.trading",
    [switch]$DryRun = $false
)

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Yellow "=== Azure Infrastructure Cleanup Script ==="
Write-ColorOutput Yellow "Resource Group: $ResourceGroupName"
Write-ColorOutput Yellow "Domain: $Domain"
Write-ColorOutput Yellow "Dry Run: $DryRun"
Write-Host ""

# Check Azure CLI installation
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-ColorOutput Red "Azure CLI not installed. Please install from: https://aka.ms/installazurecliwindows"
    exit 1
}

# Login to Azure
Write-ColorOutput Green "Step 1: Azure Login"
az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput Yellow "Please login to Azure..."
    az login
}

# Get current subscription
$subscription = az account show --query name -o tsv
Write-ColorOutput Green "Current subscription: $subscription"

# Function to confirm action
function Confirm-Action {
    param([string]$Message)
    $response = Read-Host "$Message (y/N)"
    return $response -match '^[Yy]'
}

# Phase 1: Audit existing resources
Write-ColorOutput Green "`nPhase 1: Auditing Existing Resources"

# List all resource groups
Write-ColorOutput Yellow "`nResource Groups:"
$resourceGroups = az group list --query "[?contains(name, 'food') || contains(name, 'fdx')].{Name:name, Location:location}" -o json | ConvertFrom-Json
$resourceGroups | Format-Table

# List all resources in the main resource group
if ($resourceGroups | Where-Object { $_.Name -eq $ResourceGroupName }) {
    Write-ColorOutput Yellow "`nResources in $ResourceGroupName:"
    $resources = az resource list --resource-group $ResourceGroupName --query "[].{Name:name, Type:type, Location:location}" -o json | ConvertFrom-Json
    $resources | Format-Table
}

# List App Services
Write-ColorOutput Yellow "`nApp Services:"
$appServices = az webapp list --query "[?contains(name, 'food') || contains(name, 'fdx')].{Name:name, ResourceGroup:resourceGroup, State:state}" -o json | ConvertFrom-Json
$appServices | Format-Table

# List Databases
Write-ColorOutput Yellow "`nPostgreSQL Servers:"
$pgServers = az postgres server list --query "[?contains(name, 'food') || contains(name, 'fdx')].{Name:name, ResourceGroup:resourceGroup, State:userVisibleState}" -o json | ConvertFrom-Json 2>$null
if ($pgServers) { $pgServers | Format-Table }

# List Redis Caches
Write-ColorOutput Yellow "`nRedis Caches:"
$redisCaches = az redis list --query "[?contains(name, 'food') || contains(name, 'fdx')].{Name:name, ResourceGroup:resourceGroup, ProvisioningState:provisioningState}" -o json | ConvertFrom-Json 2>$null
if ($redisCaches) { $redisCaches | Format-Table }

# List Storage Accounts
Write-ColorOutput Yellow "`nStorage Accounts:"
$storageAccounts = az storage account list --query "[?contains(name, 'food') || contains(name, 'fdx')].{Name:name, ResourceGroup:resourceGroup, Location:location}" -o json | ConvertFrom-Json
if ($storageAccounts) { $storageAccounts | Format-Table }

# List Container Registries
Write-ColorOutput Yellow "`nContainer Registries:"
$registries = az acr list --query "[?contains(name, 'food') || contains(name, 'fdx')].{Name:name, ResourceGroup:resourceGroup, LoginServer:loginServer}" -o json | ConvertFrom-Json 2>$null
if ($registries) { $registries | Format-Table }

# List DNS Zones
Write-ColorOutput Yellow "`nDNS Zones:"
$dnsZones = az network dns zone list --query "[?contains(name, '$Domain')].{Name:name, ResourceGroup:resourceGroup}" -o json | ConvertFrom-Json 2>$null
if ($dnsZones) { $dnsZones | Format-Table }

# Phase 2: Cleanup (if not dry run)
if (-not $DryRun) {
    Write-ColorOutput Green "`nPhase 2: Cleanup"
    
    if (Confirm-Action "Do you want to proceed with cleanup?") {
        
        # Clean App Services
        if ($appServices -and (Confirm-Action "Delete App Services?")) {
            foreach ($app in $appServices) {
                Write-ColorOutput Yellow "Deleting App Service: $($app.Name)"
                az webapp delete --name $app.Name --resource-group $app.ResourceGroup --yes
            }
        }
        
        # Clean Databases
        if ($pgServers -and (Confirm-Action "Delete PostgreSQL servers?")) {
            foreach ($server in $pgServers) {
                Write-ColorOutput Yellow "Deleting PostgreSQL server: $($server.Name)"
                az postgres server delete --name $server.Name --resource-group $server.ResourceGroup --yes
            }
        }
        
        # Clean Redis
        if ($redisCaches -and (Confirm-Action "Delete Redis caches?")) {
            foreach ($redis in $redisCaches) {
                Write-ColorOutput Yellow "Deleting Redis cache: $($redis.Name)"
                az redis delete --name $redis.Name --resource-group $redis.ResourceGroup --yes
            }
        }
        
        # Clean Storage Accounts
        if ($storageAccounts -and (Confirm-Action "Delete Storage accounts?")) {
            foreach ($storage in $storageAccounts) {
                Write-ColorOutput Yellow "Deleting Storage account: $($storage.Name)"
                az storage account delete --name $storage.Name --resource-group $storage.ResourceGroup --yes
            }
        }
        
        # Clean Container Registries
        if ($registries -and (Confirm-Action "Delete Container registries?")) {
            foreach ($registry in $registries) {
                Write-ColorOutput Yellow "Deleting Container registry: $($registry.Name)"
                az acr delete --name $registry.Name --resource-group $registry.ResourceGroup --yes
            }
        }
        
        # Clean entire resource group
        if ($resourceGroups | Where-Object { $_.Name -eq $ResourceGroupName }) {
            if (Confirm-Action "Delete entire resource group '$ResourceGroupName'? This will delete ALL resources in it.") {
                Write-ColorOutput Yellow "Deleting resource group: $ResourceGroupName"
                az group delete --name $ResourceGroupName --yes --no-wait
                Write-ColorOutput Green "Resource group deletion initiated (running in background)"
            }
        }
    }
} else {
    Write-ColorOutput Yellow "`nDry run mode - no changes made. Remove -DryRun flag to perform actual cleanup."
}

# Phase 3: Verification
Write-ColorOutput Green "`nPhase 3: Verification"
Write-ColorOutput Yellow "Remaining resources:"

# Check remaining resources
$remainingGroups = az group list --query "[?contains(name, 'food') || contains(name, 'fdx')].name" -o tsv
if ($remainingGroups) {
    Write-ColorOutput Yellow "Resource groups still exist: $remainingGroups"
} else {
    Write-ColorOutput Green "✓ No FoodXchange resource groups found"
}

Write-ColorOutput Green "`n=== Azure Cleanup Complete ==="
Write-ColorOutput Yellow "`nNext steps:"
Write-ColorOutput White "1. Wait for resource deletion to complete (5-10 minutes)"
Write-ColorOutput White "2. Verify in Azure Portal: https://portal.azure.com"
Write-ColorOutput White "3. Run fresh infrastructure setup script"