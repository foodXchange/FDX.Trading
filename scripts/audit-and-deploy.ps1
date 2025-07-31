# Complete Audit, Cleanup, and Fresh Deployment Script for FoodXchange
# This script audits existing resources, cleans them up, and performs fresh deployment

param(
    [string]$ResourceGroupName = "foodxchange-prod-rg",
    [string]$Location = "eastus",
    [string]$AppName = "foodxchange-app",
    [string]$Domain = "fdx.trading",
    [switch]$AuditOnly = $false,
    [switch]$Force = $false
)

# Colors
function Write-ColorOutput {
    param([string]$Color, [string]$Message)
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput Cyan "=== FoodXchange Complete Deployment Script ==="
Write-ColorOutput Yellow "Mode: $(if($AuditOnly) {'AUDIT ONLY'} else {'FULL DEPLOYMENT'})"
Write-Host ""

# Variables for new resources
$ACR_NAME = "foodxchangeacr"
$PG_SERVER = "foodxchange-pg-server"
$REDIS_NAME = "foodxchange-redis"
$STORAGE_NAME = "foodxchangestorage"
$KEYVAULT_NAME = "foodxchange-kv"
$PLAN_NAME = "foodxchange-plan"

# Arrays to store found resources
$foundResources = @{
    ResourceGroups = @()
    WebApps = @()
    PostgreSQL = @()
    Redis = @()
    Storage = @()
    ContainerRegistries = @()
    KeyVaults = @()
    AppServicePlans = @()
    DNSZones = @()
    Certificates = @()
}

# Function to confirm action
function Confirm-Action {
    param([string]$Message)
    if ($Force) { return $true }
    $response = Read-Host "$Message (y/N)"
    return $response -match '^[Yy]'
}

# Check prerequisites
Write-ColorOutput Green "Checking prerequisites..."
$missingTools = @()

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    $missingTools += "Azure CLI"
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    $missingTools += "Docker"
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    $missingTools += "GitHub CLI (optional but recommended)"
}

if ($missingTools.Count -gt 0) {
    Write-ColorOutput Red "Missing required tools: $($missingTools -join ', ')"
    Write-ColorOutput Yellow "Install commands:"
    if ($missingTools -contains "Azure CLI") {
        Write-Host "  winget install Microsoft.AzureCLI"
    }
    if ($missingTools -contains "Docker") {
        Write-Host "  Download from: https://www.docker.com/products/docker-desktop"
    }
    if ($missingTools -contains "GitHub CLI") {
        Write-Host "  winget install GitHub.cli"
    }
    if (-not $Force) { exit 1 }
}

# Login to Azure
Write-ColorOutput Green "`nChecking Azure login..."
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-ColorOutput Yellow "Please login to Azure..."
    az login
    $account = az account show | ConvertFrom-Json
}
Write-ColorOutput Green "Logged in as: $($account.user.name)"
Write-ColorOutput Green "Subscription: $($account.name)"

# PHASE 1: COMPREHENSIVE AUDIT
Write-ColorOutput Cyan "`n=== PHASE 1: COMPREHENSIVE AUDIT ==="

Write-ColorOutput Yellow "`nSearching for all FoodXchange-related resources..."

# Search for resource groups
Write-ColorOutput Green "Checking Resource Groups..."
$allGroups = az group list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" | ConvertFrom-Json
foreach ($group in $allGroups) {
    $foundResources.ResourceGroups += $group
    Write-Host "  Found: $($group.name) in $($group.location)"
}

# Search for Web Apps
Write-ColorOutput Green "`nChecking Web Apps..."
$allWebApps = az webapp list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" | ConvertFrom-Json
foreach ($app in $allWebApps) {
    $foundResources.WebApps += $app
    Write-Host "  Found: $($app.name) (State: $($app.state))"
}

# Search for PostgreSQL servers
Write-ColorOutput Green "`nChecking PostgreSQL Servers..."
$allPgServers = az postgres server list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" 2>$null | ConvertFrom-Json
foreach ($server in $allPgServers) {
    $foundResources.PostgreSQL += $server
    Write-Host "  Found: $($server.name) (State: $($server.userVisibleState))"
}

# Search for Redis caches
Write-ColorOutput Green "`nChecking Redis Caches..."
$allRedis = az redis list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" 2>$null | ConvertFrom-Json
foreach ($redis in $allRedis) {
    $foundResources.Redis += $redis
    Write-Host "  Found: $($redis.name) (State: $($redis.provisioningState))"
}

# Search for Storage accounts
Write-ColorOutput Green "`nChecking Storage Accounts..."
$allStorage = az storage account list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" | ConvertFrom-Json
foreach ($storage in $allStorage) {
    $foundResources.Storage += $storage
    Write-Host "  Found: $($storage.name)"
}

# Search for Container Registries
Write-ColorOutput Green "`nChecking Container Registries..."
$allACR = az acr list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" 2>$null | ConvertFrom-Json
foreach ($acr in $allACR) {
    $foundResources.ContainerRegistries += $acr
    Write-Host "  Found: $($acr.name) ($($acr.loginServer))"
}

# Search for Key Vaults
Write-ColorOutput Green "`nChecking Key Vaults..."
$allKeyVaults = az keyvault list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" 2>$null | ConvertFrom-Json
foreach ($kv in $allKeyVaults) {
    $foundResources.KeyVaults += $kv
    Write-Host "  Found: $($kv.name)"
}

# Search for App Service Plans
Write-ColorOutput Green "`nChecking App Service Plans..."
$allPlans = az appservice plan list --query "[?contains(name, 'food') || contains(name, 'fdx') || contains(name, 'foodxchange')]" | ConvertFrom-Json
foreach ($plan in $allPlans) {
    $foundResources.AppServicePlans += $plan
    Write-Host "  Found: $($plan.name) (SKU: $($plan.sku.name))"
}

# Search for DNS Zones
Write-ColorOutput Green "`nChecking DNS Zones..."
$allDNS = az network dns zone list --query "[?contains(name, '$Domain')]" 2>$null | ConvertFrom-Json
foreach ($dns in $allDNS) {
    $foundResources.DNSZones += $dns
    Write-Host "  Found: $($dns.name)"
}

# Summary
Write-ColorOutput Cyan "`n=== AUDIT SUMMARY ==="
Write-Host "Resource Groups: $($foundResources.ResourceGroups.Count)"
Write-Host "Web Apps: $($foundResources.WebApps.Count)"
Write-Host "PostgreSQL Servers: $($foundResources.PostgreSQL.Count)"
Write-Host "Redis Caches: $($foundResources.Redis.Count)"
Write-Host "Storage Accounts: $($foundResources.Storage.Count)"
Write-Host "Container Registries: $($foundResources.ContainerRegistries.Count)"
Write-Host "Key Vaults: $($foundResources.KeyVaults.Count)"
Write-Host "App Service Plans: $($foundResources.AppServicePlans.Count)"
Write-Host "DNS Zones: $($foundResources.DNSZones.Count)"

$totalResources = 0
foreach ($key in $foundResources.Keys) {
    $totalResources += $foundResources[$key].Count
}

if ($totalResources -eq 0) {
    Write-ColorOutput Green "`nNo existing FoodXchange resources found. Ready for fresh deployment!"
} else {
    Write-ColorOutput Yellow "`nFound $totalResources existing resources that may need cleanup."
}

if ($AuditOnly) {
    Write-ColorOutput Cyan "`nAudit complete. Run without -AuditOnly flag to proceed with cleanup and deployment."
    exit 0
}

# PHASE 2: CLEANUP
if ($totalResources -gt 0) {
    Write-ColorOutput Cyan "`n=== PHASE 2: CLEANUP ==="
    
    if (Confirm-Action "Do you want to clean up ALL found resources?") {
        
        # Delete Web Apps first (they depend on other resources)
        if ($foundResources.WebApps.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting Web Apps..."
            foreach ($app in $foundResources.WebApps) {
                Write-Host "  Deleting: $($app.name)..."
                az webapp delete --name $app.name --resource-group $app.resourceGroup --keep-empty-plan
            }
        }
        
        # Delete databases
        if ($foundResources.PostgreSQL.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting PostgreSQL Servers..."
            foreach ($server in $foundResources.PostgreSQL) {
                Write-Host "  Deleting: $($server.name)..."
                az postgres server delete --name $server.name --resource-group $server.resourceGroup --yes
            }
        }
        
        # Delete Redis caches
        if ($foundResources.Redis.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting Redis Caches..."
            foreach ($redis in $foundResources.Redis) {
                Write-Host "  Deleting: $($redis.name)..."
                az redis delete --name $redis.name --resource-group $redis.resourceGroup --yes
            }
        }
        
        # Delete Container Registries
        if ($foundResources.ContainerRegistries.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting Container Registries..."
            foreach ($acr in $foundResources.ContainerRegistries) {
                Write-Host "  Deleting: $($acr.name)..."
                az acr delete --name $acr.name --resource-group $acr.resourceGroup --yes
            }
        }
        
        # Delete Storage Accounts
        if ($foundResources.Storage.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting Storage Accounts..."
            foreach ($storage in $foundResources.Storage) {
                Write-Host "  Deleting: $($storage.name)..."
                az storage account delete --name $storage.name --resource-group $storage.resourceGroup --yes
            }
        }
        
        # Delete Key Vaults (soft delete)
        if ($foundResources.KeyVaults.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting Key Vaults..."
            foreach ($kv in $foundResources.KeyVaults) {
                Write-Host "  Deleting: $($kv.name)..."
                az keyvault delete --name $kv.name --resource-group $kv.resourceGroup
                # Purge if needed
                if (Confirm-Action "Permanently purge Key Vault $($kv.name)?") {
                    az keyvault purge --name $kv.name
                }
            }
        }
        
        # Delete App Service Plans
        if ($foundResources.AppServicePlans.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting App Service Plans..."
            foreach ($plan in $foundResources.AppServicePlans) {
                Write-Host "  Deleting: $($plan.name)..."
                az appservice plan delete --name $plan.name --resource-group $plan.resourceGroup --yes
            }
        }
        
        # Delete DNS Zones
        if ($foundResources.DNSZones.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting DNS Zones..."
            if (Confirm-Action "Delete DNS zones? This will affect domain routing!") {
                foreach ($dns in $foundResources.DNSZones) {
                    Write-Host "  Deleting: $($dns.name)..."
                    az network dns zone delete --name $dns.name --resource-group $dns.resourceGroup --yes
                }
            }
        }
        
        # Finally, delete resource groups
        if ($foundResources.ResourceGroups.Count -gt 0) {
            Write-ColorOutput Yellow "`nDeleting Resource Groups..."
            foreach ($group in $foundResources.ResourceGroups) {
                if (Confirm-Action "Delete resource group '$($group.name)'? This will delete ALL remaining resources in it.") {
                    Write-Host "  Deleting: $($group.name)..."
                    az group delete --name $group.name --yes --no-wait
                }
            }
        }
        
        Write-ColorOutput Green "`nCleanup initiated. Waiting for operations to complete..."
        Start-Sleep -Seconds 30
    }
}

# PHASE 3: FRESH DEPLOYMENT
Write-ColorOutput Cyan "`n=== PHASE 3: FRESH DEPLOYMENT ==="

if (-not (Confirm-Action "Proceed with fresh deployment?")) {
    Write-ColorOutput Yellow "Deployment cancelled."
    exit 0
}

# Run the fresh deployment script
Write-ColorOutput Green "Starting fresh deployment..."

# Create new deployment script parameters
$deployParams = @{
    ResourceGroupName = $ResourceGroupName
    Location = $Location
    AppName = $AppName
    Domain = $Domain
    SkipCleanup = $true  # We already did cleanup
}

# Execute fresh deployment
& "$PSScriptRoot\fresh-deploy.ps1" @deployParams

Write-ColorOutput Cyan "`n=== COMPLETE ==="
Write-ColorOutput Green "Audit, cleanup, and fresh deployment process completed!"