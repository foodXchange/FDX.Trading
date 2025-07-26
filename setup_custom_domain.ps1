# Quick setup script for fdx.trading domain
# Run this script after configuring DNS records in Namecheap

param(
    [string]$Domain = "fdx.trading",
    [string]$ResourceGroup = "foodxchange-rg",
    [string]$AppName = "foodxchange-app"
)

$wwwDomain = "www.$Domain"

Write-Host "🚀 Setting up custom domain: $Domain" -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Cyan
Write-Host "App Service: $AppName" -ForegroundColor Cyan

# Check if logged in to Azure
Write-Host "`nChecking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if (!$account) {
    Write-Host "❌ Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Logged in to Azure" -ForegroundColor Green

# Check if App Service exists
Write-Host "`nVerifying App Service exists..." -ForegroundColor Yellow
$appService = az webapp show --name $AppName --resource-group $ResourceGroup 2>$null
if (!$appService) {
    Write-Host "❌ App Service '$AppName' not found in resource group '$ResourceGroup'" -ForegroundColor Red
    exit 1
}

Write-Host "✅ App Service found" -ForegroundColor Green

# Get current hostname bindings
Write-Host "`nCurrent hostname bindings:" -ForegroundColor Yellow
az webapp config hostname list --webapp-name $AppName --resource-group $ResourceGroup --output table

# Add custom domains
Write-Host "`nAdding custom domains..." -ForegroundColor Yellow

try {
    # Add main domain
    Write-Host "Adding $Domain..." -ForegroundColor Cyan
    az webapp config hostname add --webapp-name $AppName --resource-group $ResourceGroup --hostname $Domain
    
    # Add www subdomain
    Write-Host "Adding $wwwDomain..." -ForegroundColor Cyan
    az webapp config hostname add --webapp-name $AppName --resource-group $ResourceGroup --hostname $wwwDomain
    
    Write-Host "✅ Custom domains added successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add custom domains: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Update CORS settings
Write-Host "`nUpdating CORS settings..." -ForegroundColor Yellow
try {
    az webapp config appsettings set --name $AppName --resource-group $ResourceGroup --settings BACKEND_CORS_ORIGINS="https://$Domain,https://$wwwDomain,http://localhost:3000,http://localhost:8000"
    Write-Host "✅ CORS settings updated" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Failed to update CORS settings. You may need to update them manually." -ForegroundColor Yellow
}

# Update email settings
Write-Host "`nUpdating email settings..." -ForegroundColor Yellow
try {
    az webapp config appsettings set --name $AppName --resource-group $ResourceGroup --settings EMAILS_FROM_EMAIL="noreply@$Domain"
    Write-Host "✅ Email settings updated" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Failed to update email settings. You may need to update them manually." -ForegroundColor Yellow
}

# Get outbound IPs for DNS A records
Write-Host "`n📋 Outbound IP addresses for DNS A records:" -ForegroundColor Yellow
$outboundIPs = az webapp show --name $AppName --resource-group $ResourceGroup --query outboundIpAddresses --output tsv
Write-Host $outboundIPs -ForegroundColor Cyan

# Get current hostname bindings after changes
Write-Host "`nUpdated hostname bindings:" -ForegroundColor Yellow
az webapp config hostname list --webapp-name $AppName --resource-group $ResourceGroup --output table

# Create backup of current settings
Write-Host "`nCreating backup of current settings..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupFile = "app-settings-backup-$timestamp.json"

try {
    az webapp config appsettings list --name $AppName --resource-group $ResourceGroup --output json > $backupFile
    Write-Host "✅ Settings backed up to: $backupFile" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Failed to create backup" -ForegroundColor Yellow
}

# Display next steps
Write-Host "`n🎉 Setup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Configure DNS records in Namecheap:" -ForegroundColor White
Write-Host "   - Type: CNAME" -ForegroundColor Gray
Write-Host "   - Name: @" -ForegroundColor Gray
Write-Host "   - Value: $AppName.azurewebsites.net" -ForegroundColor Gray
Write-Host "   - TTL: Automatic" -ForegroundColor Gray
Write-Host ""
Write-Host "   - Type: CNAME" -ForegroundColor Gray
Write-Host "   - Name: www" -ForegroundColor Gray
Write-Host "   - Value: $AppName.azurewebsites.net" -ForegroundColor Gray
Write-Host "   - TTL: Automatic" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Alternative A records (better performance):" -ForegroundColor White
Write-Host "   - Type: A" -ForegroundColor Gray
Write-Host "   - Name: @" -ForegroundColor Gray
Write-Host "   - Value: $outboundIPs" -ForegroundColor Gray
Write-Host "   - TTL: Automatic" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Wait for DNS propagation (15 minutes to 48 hours)" -ForegroundColor White
Write-Host "4. Test the new domain: https://$Domain" -ForegroundColor White
Write-Host "5. Set up SSL certificate in Azure Portal" -ForegroundColor White

Write-Host "`n📝 DNS Configuration Summary:" -ForegroundColor Cyan
Write-Host "Domain: $Domain" -ForegroundColor White
Write-Host "WWW Domain: $wwwDomain" -ForegroundColor White
Write-Host "Azure App Service: $AppName.azurewebsites.net" -ForegroundColor White
Write-Host "Outbound IPs: $outboundIPs" -ForegroundColor White

Write-Host "`n✅ Script completed successfully!" -ForegroundColor Green 