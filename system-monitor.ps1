# Food Xchange System Monitor
# Monitors all critical services and provides real-time status

param(
    [string]$BaseUrl = "http://localhost:8000",
    [switch]$Continuous,
    [int]$Interval = 30,
    [switch]$Production
)

# Override base URL for production if specified
if ($Production) {
    $BaseUrl = "https://your-site.azurewebsites.net"
}

function Write-StatusHeader {
    param([string]$Title)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
}

function Test-Service {
    param(
        [string]$ServiceName, 
        [string]$Url,
        [string]$ExpectedStatus = "200"
    )
    
    $startTime = Get-Date
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 10 -UseBasicParsing
        $endTime = Get-Date
        $responseTime = ($endTime - $startTime).TotalMilliseconds
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "[OK] $ServiceName - ONLINE" -ForegroundColor Green
            Write-Host "   Response Time: ${responseTime}ms" -ForegroundColor Gray
            Write-Host "   Status Code: $($response.StatusCode)" -ForegroundColor Gray
            return @{ Status = $true; ResponseTime = $responseTime; StatusCode = $response.StatusCode }
        } else {
            Write-Host "[WARN] $ServiceName - UNEXPECTED STATUS" -ForegroundColor Yellow
            Write-Host "   Status Code: $($response.StatusCode)" -ForegroundColor Yellow
            return @{ Status = $false; ResponseTime = $responseTime; StatusCode = $response.StatusCode }
        }
    } catch {
        $endTime = Get-Date
        $responseTime = ($endTime - $startTime).TotalMilliseconds
        Write-Host "[FAIL] $ServiceName - OFFLINE" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Response Time: ${responseTime}ms" -ForegroundColor Gray
        return @{ Status = $false; ResponseTime = $responseTime; Error = $_.Exception.Message }
    }
}

function Test-DatabaseConnection {
    param([string]$BaseUrl)
    
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl/health/db" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $content = $response.Content | ConvertFrom-Json
            Write-Host "[OK] Database - ONLINE" -ForegroundColor Green
            Write-Host "   Status: $($content.status)" -ForegroundColor Gray
            if ($content.details) {
                Write-Host "   Details: $($content.details)" -ForegroundColor Gray
            }
            return $true
        } else {
            Write-Host "❌ Database - OFFLINE" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Database - OFFLINE" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-SystemMetrics {
    param([string]$BaseUrl)
    
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl/metrics" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $content = $response.Content | ConvertFrom-Json
            Write-Host "System Metrics:" -ForegroundColor Cyan
            Write-Host "   CPU Usage: $($content.cpu_percent)%" -ForegroundColor Gray
            Write-Host "   Memory Usage: $($content.memory_percent)%" -ForegroundColor Gray
            Write-Host "   Disk Usage: $($content.disk_percent)%" -ForegroundColor Gray
            Write-Host "   Uptime: $($content.uptime)" -ForegroundColor Gray
            return $content
        }
    } catch {
        Write-Host "[WARN] Could not retrieve system metrics" -ForegroundColor Yellow
        return $null
    }
}

function Show-OverallStatus {
    param([array]$Results)
    
    $allOnline = $Results | Where-Object { $_.Status -eq $true }
    $offline = $Results | Where-Object { $_.Status -eq $false }
    
    Write-Host "`n" -NoNewline
    Write-Host "Overall System Status:" -ForegroundColor Yellow
    Write-Host "   Online Services: $($allOnline.Count)/$($Results.Count)" -ForegroundColor White
    
    if ($offline.Count -gt 0) {
        Write-Host "   Offline Services: $($offline.Count)" -ForegroundColor Red
        Write-Host "   Affected Services:" -ForegroundColor Red
        foreach ($service in $offline) {
            Write-Host "     - $($service.ServiceName)" -ForegroundColor Red
        }
    }
    
    if ($allOnline.Count -eq $Results.Count) {
        Write-Host "[ALL OK] All Systems Operational" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[ISSUES] System Issues Detected" -ForegroundColor Red
        return $false
    }
}

function Monitor-Services {
    param([string]$BaseUrl)
    
    Write-StatusHeader "Food Xchange System Status - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    
    $results = @()
    
    # Test main website
    $webResult = Test-Service "Main Website" "$BaseUrl/health"
    $webResult.ServiceName = "Main Website"
    $results += $webResult
    
    # Test database
    $dbResult = Test-Service "Database" "$BaseUrl/health/detailed"
    $dbResult.ServiceName = "Database"
    $results += $dbResult
    
    # Test API endpoints
    $apiResult = Test-Service "API Endpoints" "$BaseUrl/docs"
    $apiResult.ServiceName = "API Endpoints"
    $results += $apiResult
    
    # Test Azure Monitor (if available)
    $azureResult = Test-Service "Azure Monitor" "$BaseUrl/monitoring/azure"
    $azureResult.ServiceName = "Azure Monitor"
    $results += $azureResult
    
    # Test authentication
    $authResult = Test-Service "Authentication" "$BaseUrl/login"
    $authResult.ServiceName = "Authentication"
    $results += $authResult
    
    # Test static files
    $staticResult = Test-Service "Static Files" "$BaseUrl/static/css/components.css"
    $staticResult.ServiceName = "Static Files"
    $results += $staticResult
    
    # Get system metrics
    Get-SystemMetrics -BaseUrl $BaseUrl
    
    # Show overall status
    $allHealthy = Show-OverallStatus -Results $results
    
    return @{
        Timestamp = Get-Date
        AllHealthy = $allHealthy
        Results = $results
    }
}

# Main execution
if ($Continuous) {
    Write-Host "Starting continuous monitoring..." -ForegroundColor Cyan
    Write-Host "   Interval: ${Interval} seconds" -ForegroundColor Gray
    Write-Host "   Base URL: $BaseUrl" -ForegroundColor Gray
    Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
    
    while ($true) {
        try {
            Monitor-Services -BaseUrl $BaseUrl
            Start-Sleep -Seconds $Interval
        } catch {
            Write-Host "[ERROR] Monitoring error: $($_.Exception.Message)" -ForegroundColor Red
            Start-Sleep -Seconds $Interval
        }
    }
} else {
    Monitor-Services -BaseUrl $BaseUrl
}

Write-Host "`nMonitoring completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan 