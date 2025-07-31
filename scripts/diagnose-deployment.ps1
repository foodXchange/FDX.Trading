# Diagnose Current Deployment Status
# This script checks the current state of your FoodXchange deployment

param(
    [string]$Domain = "fdx.trading",
    [string]$ResourceGroup = "foodxchange-prod-rg",
    [string]$AppName = "foodxchange-app"
)

function Write-ColorOutput {
    param([string]$Color, [string]$Message)
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput Cyan "=== FoodXchange Deployment Diagnosis ==="
Write-Host ""

# Check Azure CLI login
Write-ColorOutput Green "Checking Azure connection..."
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "✅ Logged in as: $($account.user.name)"
    Write-Host "✅ Subscription: $($account.name)"
} catch {
    Write-ColorOutput Red "❌ Not logged in to Azure. Run: az login"
    exit 1
}

# Check if resource group exists
Write-ColorOutput Green "`nChecking Resource Group..."
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "true") {
    Write-Host "✅ Resource Group '$ResourceGroup' exists"
    
    # List all resources in the group
    $resources = az resource list --resource-group $ResourceGroup | ConvertFrom-Json
    Write-Host "📋 Resources in group:"
    foreach ($resource in $resources) {
        Write-Host "   - $($resource.name) ($($resource.type))"
    }
} else {
    Write-ColorOutput Red "❌ Resource Group '$ResourceGroup' does not exist"
}

# Check Web App status
Write-ColorOutput Green "`nChecking Web App..."
try {
    $webapp = az webapp show --name $AppName --resource-group $ResourceGroup | ConvertFrom-Json
    Write-Host "✅ Web App '$AppName' exists"
    Write-Host "   State: $($webapp.state)"
    Write-Host "   Default hostname: $($webapp.defaultHostName)"
    Write-Host "   Resource group: $($webapp.resourceGroup)"
    
    # Check custom domains
    $hostnames = az webapp config hostname list --webapp-name $AppName --resource-group $ResourceGroup | ConvertFrom-Json
    if ($hostnames.Count -gt 0) {
        Write-Host "🌐 Custom domains configured:"
        foreach ($hostname in $hostnames) {
            Write-Host "   - $($hostname.name)"
        }
    } else {
        Write-ColorOutput Yellow "⚠️  No custom domains configured"
    }
    
} catch {
    Write-ColorOutput Red "❌ Web App '$AppName' not found or inaccessible"
}

# Check DNS configuration
Write-ColorOutput Green "`nChecking DNS..."
Write-Host "🔍 Checking DNS resolution for $Domain:"

# Check current DNS records  
try {
    $dnsResult = nslookup $Domain 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $Domain resolves"
        Write-Host $dnsResult
    } else {
        Write-ColorOutput Red "❌ $Domain does not resolve"
    }
} catch {
    Write-ColorOutput Red "❌ DNS lookup failed for $Domain"
}

Write-Host "`n🔍 Checking DNS resolution for www.$Domain:"
try {
    $wwwDnsResult = nslookup "www.$Domain" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ www.$Domain resolves"
        Write-Host $wwwDnsResult
    } else {
        Write-ColorOutput Red "❌ www.$Domain does not resolve (THIS IS THE ISSUE!)"
    }
} catch {
    Write-ColorOutput Red "❌ DNS lookup failed for www.$Domain"
}

# Check Azure DNS zones
Write-ColorOutput Green "`nChecking Azure DNS zones..."
try {
    $dnsZones = az network dns zone list --query "[?name=='$Domain']" | ConvertFrom-Json
    if ($dnsZones.Count -gt 0) {
        foreach ($zone in $dnsZones) {
            Write-Host "✅ DNS Zone: $($zone.name)"
            Write-Host "   Resource Group: $($zone.resourceGroup)"
            
            # Check A records
            $aRecords = az network dns record-set a list --zone-name $Domain --resource-group $zone.resourceGroup | ConvertFrom-Json
            if ($aRecords.Count -gt 0) {
                Write-Host "📋 A Records:"
                foreach ($record in $aRecords) {
                    Write-Host "   - $($record.name): $($record.aRecords.ipv4Address -join ', ')"
                }
            } else {
                Write-ColorOutput Yellow "⚠️  No A records found"
            }
        }
    } else {
        Write-ColorOutput Yellow "⚠️  No Azure DNS zones found for $Domain"
    }
} catch {
    Write-ColorOutput Yellow "⚠️  Could not check Azure DNS zones"
}

# Check web app accessibility
Write-ColorOutput Green "`nChecking Web App accessibility..."
if ($webapp) {
    $azureUrl = "https://$($webapp.defaultHostName)"
    Write-Host "🌐 Testing Azure URL: $azureUrl"
    
    try {
        $response = Invoke-WebRequest $azureUrl -UseBasicParsing -TimeoutSec 10
        Write-Host "✅ Azure URL responds: $($response.StatusCode)"
    } catch {
        Write-ColorOutput Red "❌ Azure URL not accessible: $($_.Exception.Message)"
    }
    
    # Test health endpoint
    try {
        $healthUrl = "$azureUrl/health"
        $healthResponse = Invoke-WebRequest $healthUrl -UseBasicParsing -TimeoutSec 10
        Write-Host "✅ Health endpoint responds: $($healthResponse.StatusCode)"
    } catch {
        Write-ColorOutput Red "❌ Health endpoint not accessible: $($_.Exception.Message)"
    }
}

# Summary and recommendations
Write-ColorOutput Cyan "`n=== DIAGNOSIS SUMMARY ==="

$issues = @()
$recommendations = @()

if ($rgExists -ne "true") {
    $issues += "Resource Group missing"
    $recommendations += "Run deployment script to create infrastructure"
}

if (-not $webapp) {
    $issues += "Web App not found"
    $recommendations += "Deploy application to Azure"
} elseif ($webapp.state -ne "Running") {
    $issues += "Web App not running"
    $recommendations += "Start the Web App: az webapp start --name $AppName --resource-group $ResourceGroup"
}

if ($hostnames.Count -eq 0) {
    $issues += "No custom domains configured"
    $recommendations += "Add custom domain: az webapp config hostname add --webapp-name $AppName --resource-group $ResourceGroup --hostname www.$Domain"
}

# The main issue is likely DNS
$issues += "DNS not resolving for www.$Domain"
$recommendations += "Configure DNS records to point to Azure"
$recommendations += "Either use Azure DNS or configure external DNS provider"

Write-ColorOutput Red "🚨 Issues found:"
foreach ($issue in $issues) {
    Write-Host "   - $issue"
}

Write-ColorOutput Green "`n💡 Recommendations:"
foreach ($rec in $recommendations) {
    Write-Host "   - $rec"
}

Write-ColorOutput Yellow "`n📋 Next Steps:"
Write-Host "1. Run the redeployment script to fix infrastructure"
Write-Host "2. Configure DNS properly (see DNS configuration guide)"
Write-Host "3. Add custom domain to Web App"
Write-Host "4. Configure SSL certificate"

Write-Host "`n" 
Write-ColorOutput Cyan "Run this to redeploy: .\scripts\redeploy-fix.ps1"