Write-Host "=== FDX-Trading Deployment Monitor ===" -ForegroundColor Cyan
Write-Host "Starting monitoring at $(Get-Date)" -ForegroundColor Gray

$azureUrl = "https://foodxchange-app.azurewebsites.net"
$customDomain = "https://fdx-trading.com"
$wwwDomain = "https://www.fdx-trading.com"

Write-Host "`n[1] Checking Azure App Service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $azureUrl -Method Head -TimeoutSec 10 -ErrorAction Stop
    Write-Host "[OK] Azure app is UP! (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Azure app is DOWN (503 Service Unavailable)" -ForegroundColor Red
    Write-Host "  This means deployment is still in progress or app failed to start" -ForegroundColor Gray
}

Write-Host "`n[2] Checking DNS Resolution..." -ForegroundColor Yellow
$dnsResult = Resolve-DnsName -Name "fdx-trading.com" -ErrorAction SilentlyContinue
if ($dnsResult) {
    Write-Host "[OK] DNS is resolving!" -ForegroundColor Green
    $dnsResult | Format-Table -AutoSize
} else {
    Write-Host "[FAIL] DNS not propagated yet" -ForegroundColor Red
    Write-Host "  DNS records are configured but propagation takes 15-60 minutes" -ForegroundColor Gray
}

Write-Host "`n[3] Checking Custom Domains..." -ForegroundColor Yellow
@($customDomain, $wwwDomain) | ForEach-Object {
    try {
        $response = Invoke-WebRequest -Uri $_ -Method Head -TimeoutSec 5 -ErrorAction Stop
        Write-Host "[OK] $_ is accessible!" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] $_ not accessible yet" -ForegroundColor Red
    }
}

Write-Host "`n[4] Next Steps:" -ForegroundColor Cyan
if ((Invoke-WebRequest -Uri $azureUrl -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue).StatusCode -ne 200) {
    Write-Host "- Wait for GitHub Actions deployment to complete (check https://github.com/foodXchange/FDX.Trading/actions)" -ForegroundColor White
    Write-Host "- If deployment fails, run: .\restart-azure-app.ps1" -ForegroundColor White
}

if (-not (Resolve-DnsName -Name "fdx-trading.com" -ErrorAction SilentlyContinue)) {
    Write-Host "- Wait for DNS propagation (15-60 minutes)" -ForegroundColor White
    Write-Host "- Check propagation status at: https://www.whatsmydns.net/#CNAME/fdx-trading.com" -ForegroundColor White
}

Write-Host "`nPress any key to refresh status..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")