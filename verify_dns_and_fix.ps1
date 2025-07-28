# FoodXchange DNS Verification and Fix Script
# Checks and fixes DNS routing for fdx.trading

Write-Host "=== FoodXchange DNS Verification ===" -ForegroundColor Cyan
Write-Host "Checking DNS configuration for fdx.trading" -ForegroundColor Yellow

# 1. Check DNS resolution
Write-Host "`n[1/5] Checking DNS resolution..." -ForegroundColor Green
try {
    $dnsResult = Resolve-DnsName -Name "www.fdx.trading" -Type A -ErrorAction Stop
    Write-Host "✓ DNS resolves to:" -ForegroundColor Green
    $dnsResult | ForEach-Object {
        Write-Host "  IP: $($_.IPAddress)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "× DNS resolution failed" -ForegroundColor Red
    Write-Host "  This means the domain is not properly configured" -ForegroundColor Yellow
}

# 2. Check CNAME records
Write-Host "`n[2/5] Checking CNAME records..." -ForegroundColor Green
try {
    $cnameResult = Resolve-DnsName -Name "www.fdx.trading" -Type CNAME -ErrorAction SilentlyContinue
    if ($cnameResult) {
        Write-Host "✓ CNAME found:" -ForegroundColor Green
        Write-Host "  Points to: $($cnameResult.NameHost)" -ForegroundColor Cyan
    } else {
        Write-Host "× No CNAME record found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "× No CNAME record found" -ForegroundColor Yellow
}

# 3. Check Azure endpoint
Write-Host "`n[3/5] Checking Azure endpoint..." -ForegroundColor Green
$azureUrl = "https://foodxchange.azurewebsites.net"
try {
    $response = Invoke-WebRequest -Uri $azureUrl -Method Head -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✓ Azure endpoint is responding: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "× Azure endpoint not responding" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. Check custom domain configuration in Azure
Write-Host "`n[4/5] Checking Azure custom domain configuration..." -ForegroundColor Green
$ResourceGroup = "foodxchange-rg"
$AppName = "foodxchange"

$customDomains = az webapp config hostname list `
    --resource-group $ResourceGroup `
    --webapp-name $AppName `
    --query "[].name" -o tsv 2>$null

if ($customDomains) {
    Write-Host "✓ Custom domains configured in Azure:" -ForegroundColor Green
    $customDomains | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor Cyan
    }
} else {
    Write-Host "× No custom domains configured in Azure" -ForegroundColor Red
}

# 5. DNS Configuration Instructions
Write-Host "`n[5/5] DNS Configuration Requirements" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "`nFor your DNS provider, you need to configure:" -ForegroundColor Yellow
Write-Host "`n1. CNAME Record for www subdomain:" -ForegroundColor Green
Write-Host "   Host/Name: www" -ForegroundColor White
Write-Host "   Points to: foodxchange.azurewebsites.net" -ForegroundColor White
Write-Host "   TTL: 3600 (or 1 hour)" -ForegroundColor White

Write-Host "`n2. A Record for root domain (fdx.trading):" -ForegroundColor Green
Write-Host "   Host/Name: @ (or leave blank)" -ForegroundColor White
Write-Host "   Points to: 20.119.56.1" -ForegroundColor White
Write-Host "   TTL: 3600 (or 1 hour)" -ForegroundColor White

Write-Host "`n3. TXT Record for domain verification:" -ForegroundColor Green
Write-Host "   Host/Name: asuid" -ForegroundColor White
Write-Host "   Value: (get from Azure Portal > Custom domains)" -ForegroundColor White
Write-Host "   TTL: 3600" -ForegroundColor White

Write-Host "`n=== Quick Fix Steps ===" -ForegroundColor Cyan
Write-Host "1. Log in to your DNS provider (GoDaddy, Namecheap, etc.)" -ForegroundColor Yellow
Write-Host "2. Add the CNAME record for www as shown above" -ForegroundColor Yellow
Write-Host "3. Add the A record for root domain as shown above" -ForegroundColor Yellow
Write-Host "4. Wait 5-30 minutes for DNS propagation" -ForegroundColor Yellow
Write-Host "5. Run this script again to verify" -ForegroundColor Yellow

# Offer to add custom domain to Azure
Write-Host "`nWould you like to add the custom domain to Azure now? (Y/N)" -ForegroundColor Cyan
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`nAdding custom domains to Azure..." -ForegroundColor Green
    
    # Add www.fdx.trading
    az webapp config hostname add `
        --resource-group $ResourceGroup `
        --webapp-name $AppName `
        --hostname "www.fdx.trading" 2>$null
    
    # Add fdx.trading
    az webapp config hostname add `
        --resource-group $ResourceGroup `
        --webapp-name $AppName `
        --hostname "fdx.trading" 2>$null
    
    Write-Host "✓ Custom domains added to Azure" -ForegroundColor Green
    Write-Host "Note: They won't work until DNS is properly configured" -ForegroundColor Yellow
}