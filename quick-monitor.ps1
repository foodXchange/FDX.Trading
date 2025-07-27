# FoodXchange Quick System Monitor
# Run this script to quickly check system status

param(
    [int]$Interval = 30,  # Check interval in seconds
    [int]$Duration = 300  # Total monitoring duration in seconds
)

Write-Host "🔍 FoodXchange Quick System Monitor" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Interval: $Interval seconds" -ForegroundColor Yellow
Write-Host "Duration: $Duration seconds" -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date
$endTime = $startTime.AddSeconds($Duration)
$cycleCount = 0

function Get-SystemStatus {
    param()
    
    $status = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        CPU = [math]::Round((Get-Counter "\Processor(_Total)\% Processor Time").CounterSamples[0].CookedValue, 2)
        Memory = [math]::Round((Get-Counter "\Memory\% Committed Bytes In Use").CounterSamples[0].CookedValue, 2)
        Disk = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" } | ForEach-Object {
            [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 2)
        }
        Network = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Measure-Object | Select-Object -ExpandProperty Count
        Processes = (Get-Process).Count
        Uptime = (Get-Date) - (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
    }
    
    return $status
}

function Test-DatabaseConnection {
    param()
    
    try {
        $databaseUrl = $env:DATABASE_URL
        if (-not $databaseUrl) {
            return @{ Status = "Not Configured"; Error = "DATABASE_URL not found" }
        }
        
        # Simple connection test using Python
        $testScript = @"
import os
import sys
from sqlalchemy import create_engine, text

try:
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print('DATABASE_URL not found')
        sys.exit(1)
    
    engine = create_engine(database_url)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test, NOW() as timestamp'))
        row = result.fetchone()
        print(f'SUCCESS: {row.timestamp}')
        sys.exit(0)
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
"@
        
        $testScript | python - 2>&1 | Out-String | ForEach-Object { $_.Trim() }
        
        if ($LASTEXITCODE -eq 0) {
            return @{ Status = "Healthy"; Response = $_ }
        } else {
            return @{ Status = "Error"; Error = $_ }
        }
    }
    catch {
        return @{ Status = "Error"; Error = $_.Exception.Message }
    }
}

function Test-AzureServices {
    param()
    
    $services = @{}
    
    # Test Azure OpenAI
    try {
        $openaiEndpoint = $env:AZURE_OPENAI_ENDPOINT
        $openaiKey = $env:AZURE_OPENAI_API_KEY
        
        if ($openaiEndpoint -and $openaiKey) {
            $headers = @{ 'api-key' = $openaiKey }
            $response = Invoke-RestMethod -Uri "$openaiEndpoint/openai/deployments" -Headers $headers -Method Get -TimeoutSec 10
            $services.OpenAI = @{ Status = "Healthy" }
        } else {
            $services.OpenAI = @{ Status = "Not Configured" }
        }
    }
    catch {
        $services.OpenAI = @{ Status = "Error"; Error = $_.Exception.Message }
    }
    
    # Test Azure Storage
    try {
        $storageConnString = $env:AZURE_STORAGE_CONNECTION_STRING
        if ($storageConnString) {
            # Simple test - try to parse connection string
            if ($storageConnString -match "AccountName=") {
                $services.Storage = @{ Status = "Configured" }
            } else {
                $services.Storage = @{ Status = "Invalid Config" }
            }
        } else {
            $services.Storage = @{ Status = "Not Configured" }
        }
    }
    catch {
        $services.Storage = @{ Status = "Error"; Error = $_.Exception.Message }
    }
    
    return $services
}

function Test-ApplicationHealth {
    param()
    
    $health = @{}
    
    try {
        $baseUrl = $env:APP_BASE_URL
        if (-not $baseUrl) { $baseUrl = "http://localhost:8000" }
        
        # Test health endpoint
        try {
            $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method Get -TimeoutSec 5
            $health.Health = @{ Status = "Healthy"; StatusCode = $response.StatusCode }
        }
        catch {
            $health.Health = @{ Status = "Error"; Error = $_.Exception.Message }
        }
        
        # Test API endpoint
        try {
            $response = Invoke-WebRequest -Uri "$baseUrl/api/v1/status" -Method Get -TimeoutSec 5
            $health.API = @{ Status = "Healthy"; StatusCode = $response.StatusCode }
        }
        catch {
            $health.API = @{ Status = "Error"; Error = $_.Exception.Message }
        }
    }
    catch {
        $health.Overall = @{ Status = "Error"; Error = $_.Exception.Message }
    }
    
    return $health
}

function Write-StatusReport {
    param(
        [hashtable]$SystemStatus,
        [hashtable]$DatabaseStatus,
        [hashtable]$AzureServices,
        [hashtable]$AppHealth
    )
    
    $cycleCount++
    $elapsed = (Get-Date) - $startTime
    
    Write-Host "`n=== Cycle #$cycleCount ($($elapsed.TotalSeconds.ToString('F0'))s elapsed) ===" -ForegroundColor Green
    Write-Host "Timestamp: $($SystemStatus.Timestamp)" -ForegroundColor Gray
    
    # System metrics
    Write-Host "`n📊 SYSTEM METRICS:" -ForegroundColor Cyan
    Write-Host "  CPU Usage: $($SystemStatus.CPU)%" -ForegroundColor $(if ($SystemStatus.CPU -gt 80) { "Red" } elseif ($SystemStatus.CPU -gt 60) { "Yellow" } else { "Green" })
    Write-Host "  Memory Usage: $($SystemStatus.Memory)%" -ForegroundColor $(if ($SystemStatus.Memory -gt 85) { "Red" } elseif ($SystemStatus.Memory -gt 70) { "Yellow" } else { "Green" })
    Write-Host "  Disk Usage: $($SystemStatus.Disk)%" -ForegroundColor $(if ($SystemStatus.Disk -gt 90) { "Red" } elseif ($SystemStatus.Disk -gt 80) { "Yellow" } else { "Green" })
    Write-Host "  Active Network Interfaces: $($SystemStatus.Network)" -ForegroundColor Green
    Write-Host "  Running Processes: $($SystemStatus.Processes)" -ForegroundColor Green
    Write-Host "  System Uptime: $($SystemStatus.Uptime.Days)d $($SystemStatus.Uptime.Hours)h $($SystemStatus.Uptime.Minutes)m" -ForegroundColor Green
    
    # Database status
    Write-Host "`n🗄️  DATABASE:" -ForegroundColor Cyan
    Write-Host "  Status: $($DatabaseStatus.Status)" -ForegroundColor $(if ($DatabaseStatus.Status -eq "Healthy") { "Green" } elseif ($DatabaseStatus.Status -eq "Not Configured") { "Yellow" } else { "Red" })
    if ($DatabaseStatus.Error) {
        Write-Host "  Error: $($DatabaseStatus.Error)" -ForegroundColor Red
    }
    if ($DatabaseStatus.Response) {
        Write-Host "  Response: $($DatabaseStatus.Response)" -ForegroundColor Green
    }
    
    # Azure services
    Write-Host "`n☁️  AZURE SERVICES:" -ForegroundColor Cyan
    foreach ($service in $AzureServices.GetEnumerator()) {
        $color = if ($service.Value.Status -eq "Healthy") { "Green" } elseif ($service.Value.Status -eq "Not Configured") { "Yellow" } else { "Red" }
        Write-Host "  $($service.Key): $($service.Value.Status)" -ForegroundColor $color
        if ($service.Value.Error) {
            Write-Host "    Error: $($service.Value.Error)" -ForegroundColor Red
        }
    }
    
    # Application health
    Write-Host "`n🌐 APPLICATION:" -ForegroundColor Cyan
    foreach ($endpoint in $AppHealth.GetEnumerator()) {
        $color = if ($endpoint.Value.Status -eq "Healthy") { "Green" } else { "Red" }
        Write-Host "  $($endpoint.Key): $($endpoint.Value.Status)" -ForegroundColor $color
        if ($endpoint.Value.StatusCode) {
            Write-Host "    Status Code: $($endpoint.Value.StatusCode)" -ForegroundColor Gray
        }
        if ($endpoint.Value.Error) {
            Write-Host "    Error: $($endpoint.Value.Error)" -ForegroundColor Red
        }
    }
    
    # Overall status
    $criticalIssues = 0
    if ($SystemStatus.CPU -gt 90) { $criticalIssues++ }
    if ($SystemStatus.Memory -gt 90) { $criticalIssues++ }
    if ($SystemStatus.Disk -gt 95) { $criticalIssues++ }
    if ($DatabaseStatus.Status -eq "Error") { $criticalIssues++ }
    
    Write-Host "`n📈 OVERALL STATUS:" -ForegroundColor Cyan
    if ($criticalIssues -eq 0) {
        Write-Host "  ✅ SYSTEM HEALTHY" -ForegroundColor Green
    } elseif ($criticalIssues -le 2) {
        Write-Host "  ⚠️  SYSTEM DEGRADED ($criticalIssues issues)" -ForegroundColor Yellow
    } else {
        Write-Host "  🚨 SYSTEM CRITICAL ($criticalIssues issues)" -ForegroundColor Red
    }
}

# Main monitoring loop
Write-Host "Starting monitoring... Press Ctrl+C to stop early" -ForegroundColor Yellow
Write-Host ""

try {
    while ((Get-Date) -lt $endTime) {
        $systemStatus = Get-SystemStatus
        $databaseStatus = Test-DatabaseConnection
        $azureServices = Test-AzureServices
        $appHealth = Test-ApplicationHealth
        
        Write-StatusReport -SystemStatus $systemStatus -DatabaseStatus $databaseStatus -AzureServices $azureServices -AppHealth $appHealth
        
        $remaining = $endTime - (Get-Date)
        if ($remaining.TotalSeconds -gt 0) {
            Write-Host "`n⏳ Next check in $Interval seconds... (Monitoring ends in $($remaining.TotalSeconds.ToString('F0'))s)" -ForegroundColor Gray
            Start-Sleep -Seconds $Interval
        }
    }
}
catch {
    Write-Host "`n❌ Monitoring interrupted: $($_.Exception.Message)" -ForegroundColor Red
}

$totalTime = (Get-Date) - $startTime
Write-Host "`n✅ Monitoring completed!" -ForegroundColor Green
Write-Host "Total cycles: $cycleCount" -ForegroundColor Cyan
Write-Host "Total time: $($totalTime.TotalMinutes.ToString('F1')) minutes" -ForegroundColor Cyan
Write-Host "Average cycle time: $(($totalTime.TotalSeconds / $cycleCount).ToString('F1')) seconds" -ForegroundColor Cyan