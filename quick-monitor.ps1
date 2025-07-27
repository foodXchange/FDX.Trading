# Quick FoodXchange Monitor
# Simple script to quickly check if all services are running

Write-Host "FoodXchange Quick Status Check" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Default to localhost
$baseUrl = "http://localhost:8000"

# Check if app is running
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    Write-Host "[OK] App Status: ONLINE" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] App Status: OFFLINE" -ForegroundColor Red
    Write-Host "   Make sure to run: quick_start.bat" -ForegroundColor Yellow
    exit 1
}

# Check database
try {
    $dbHealth = Invoke-RestMethod -Uri "$baseUrl/health/detailed" -TimeoutSec 5
    if ($dbHealth.database -match "healthy") {
        Write-Host "[OK] Database: CONNECTED" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Database: ISSUES" -ForegroundColor Yellow
        Write-Host "   Status: $($dbHealth.database)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[FAIL] Database Check: FAILED" -ForegroundColor Red
}

# Check API docs
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -TimeoutSec 5
    Write-Host "[OK] API Docs: AVAILABLE" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] API Docs: UNAVAILABLE" -ForegroundColor Red
}

# Check Azure Monitor
try {
    $azureMonitor = Invoke-RestMethod -Uri "$baseUrl/monitoring/azure" -TimeoutSec 5
    if ($azureMonitor.azure_monitor.enabled) {
        Write-Host "[OK] Azure Monitor: ENABLED" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Azure Monitor: NOT CONFIGURED" -ForegroundColor Gray
    }
} catch {
    Write-Host "[INFO] Azure Monitor: NOT AVAILABLE" -ForegroundColor Gray
}

Write-Host "`nAccess Points:" -ForegroundColor Yellow
Write-Host "   Main App: $baseUrl" -ForegroundColor White
Write-Host "   API Docs: $baseUrl/docs" -ForegroundColor White
Write-Host "   Health: $baseUrl/health" -ForegroundColor White

Write-Host "`nQuick check complete!" -ForegroundColor Green