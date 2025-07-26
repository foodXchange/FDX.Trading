# Test PostgreSQL connectivity from Windows

Write-Host "Testing Azure PostgreSQL Connectivity..." -ForegroundColor Cyan

# Test DNS resolution
Write-Host "`nDNS Resolution Test:" -ForegroundColor Yellow
$hostname = "foodxchangepgfr.postgres.database.azure.com"
try {
    $ip = [System.Net.Dns]::GetHostAddresses($hostname)
    Write-Host "  Resolved $hostname to: $($ip.IPAddressToString)" -ForegroundColor Green
} catch {
    Write-Host "  Failed to resolve $hostname" -ForegroundColor Red
}

# Test TCP connectivity
Write-Host "`nTCP Connection Test:" -ForegroundColor Yellow
$connection = Test-NetConnection -ComputerName $hostname -Port 5432
if ($connection.TcpTestSucceeded) {
    Write-Host "  TCP connection to port 5432: SUCCESS" -ForegroundColor Green
} else {
    Write-Host "  TCP connection to port 5432: FAILED" -ForegroundColor Red
    Write-Host "  This indicates a firewall issue" -ForegroundColor Red
}

# Show route
Write-Host "`nNetwork Route:" -ForegroundColor Yellow
tracert -h 5 $hostname

Write-Host "`nYour Public IP:" -ForegroundColor Yellow
$publicIP = (Invoke-WebRequest -Uri "https://api.ipify.org").Content
Write-Host "  $publicIP" -ForegroundColor Cyan
Write-Host "`nMake sure this IP is added to Azure PostgreSQL firewall rules!" -ForegroundColor Yellow