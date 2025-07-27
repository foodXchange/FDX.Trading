# Run all safe PowerShell scripts in FoodXchange
Write-Host "Running All Safe PowerShell Scripts" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# 1. Quick Monitor (Safe - checks local services)
Write-Host "`n1. Running Quick Monitor..." -ForegroundColor Yellow
try {
    & ".\quick-monitor.ps1"
} catch {
    Write-Host "[ERROR] Failed to run quick-monitor.ps1: $_" -ForegroundColor Red
}

# 2. System Monitor (Safe - checks services)
Write-Host "`n2. Running System Monitor (Single Run)..." -ForegroundColor Yellow
try {
    & ".\system-monitor.ps1"
} catch {
    Write-Host "[ERROR] Failed to run system-monitor.ps1: $_" -ForegroundColor Red
}

# 3. PostgreSQL Connectivity Test (Safe - just tests connection)
Write-Host "`n3. Testing PostgreSQL Connectivity..." -ForegroundColor Yellow
try {
    & ".\test_postgres_connectivity.ps1"
} catch {
    Write-Host "[ERROR] Failed to run test_postgres_connectivity.ps1: $_" -ForegroundColor Red
}

Write-Host "`n=== Summary of Scripts That Require Azure Login ===" -ForegroundColor Cyan
Write-Host "The following scripts require Azure CLI login to run:" -ForegroundColor Yellow
Write-Host "- add_firewall_rule.ps1 (Adds your IP to Azure PostgreSQL firewall)" -ForegroundColor White
Write-Host "- azure-deploy.ps1 (Deploys app to Azure App Service)" -ForegroundColor White
Write-Host "- create_azure_services.ps1 (Creates Azure resources)" -ForegroundColor White
Write-Host "- setup_azure_monitor.ps1 (Sets up Application Insights)" -ForegroundColor White

Write-Host "`n=== Scripts That Require Parameters ===" -ForegroundColor Cyan
Write-Host "- integrate-v0-component.ps1 -ComponentName 'component-name'" -ForegroundColor White
Write-Host "- integrate-v0-simple.ps1 -HtmlFile 'path/to/file.html'" -ForegroundColor White

Write-Host "`nAll safe scripts completed!" -ForegroundColor Green