# FoodXchange Monitoring Service Setup
# Creates a Windows scheduled task for continuous monitoring

param(
    [switch]$Remove,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status
)

$ErrorActionPreference = "Stop"

# Check for admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script requires Administrator privileges. Please run as Administrator."
    exit 1
}

$taskName = "FoodXchange_Continuous_Monitor"
$scriptPath = Join-Path $PSScriptRoot "automated_monitor.py"
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path

if (-not $pythonPath) {
    Write-Error "Python not found in PATH"
    exit 1
}

if ($Remove) {
    Write-Host "Removing monitoring service..." -ForegroundColor Yellow
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "Monitoring service removed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Service not found or already removed" -ForegroundColor Gray
    }
    exit 0
}

if ($Stop) {
    Write-Host "Stopping monitoring service..." -ForegroundColor Yellow
    try {
        Stop-ScheduledTask -TaskName $taskName
        Write-Host "Monitoring service stopped" -ForegroundColor Green
    } catch {
        Write-Error "Failed to stop service: $_"
    }
    exit 0
}

if ($Start) {
    Write-Host "Starting monitoring service..." -ForegroundColor Yellow
    try {
        Start-ScheduledTask -TaskName $taskName
        Write-Host "Monitoring service started" -ForegroundColor Green
    } catch {
        Write-Error "Failed to start service: $_"
    }
    exit 0
}

if ($Status) {
    try {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
        $info = Get-ScheduledTaskInfo -TaskName $taskName
        
        Write-Host "`nMonitoring Service Status" -ForegroundColor Cyan
        Write-Host "=========================" -ForegroundColor Cyan
        Write-Host "State: $($task.State)"
        Write-Host "Last Run: $($info.LastRunTime)"
        Write-Host "Last Result: $($info.LastTaskResult)"
        Write-Host "Next Run: $($info.NextRunTime)"
        
        # Check if monitor is actually running
        $monitorProcess = Get-Process python -ErrorAction SilentlyContinue | 
            Where-Object {$_.CommandLine -like "*automated_monitor.py*"}
        
        if ($monitorProcess) {
            Write-Host "Monitor Process: Running (PID: $($monitorProcess.Id))" -ForegroundColor Green
        } else {
            Write-Host "Monitor Process: Not Running" -ForegroundColor Red
        }
    } catch {
        Write-Host "Monitoring service not installed" -ForegroundColor Red
    }
    exit 0
}

# Create the monitoring service
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  FoodXchange Monitoring Service Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Remove existing task if present
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# Create action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`""

# Create trigger (start at system startup and keep running)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -Priority 4

# Set to run as SYSTEM with highest privileges
$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# Register the task
$task = Register-ScheduledTask `
    -TaskName $taskName `
    -Description "Continuous monitoring service for FoodXchange system health" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force

Write-Host "`nMonitoring service created successfully!" -ForegroundColor Green

# Start the service
Write-Host "`nStarting monitoring service..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName $taskName

Start-Sleep -Seconds 3

# Check status
$info = Get-ScheduledTaskInfo -TaskName $taskName
if ($task.State -eq "Running") {
    Write-Host "Monitoring service is running!" -ForegroundColor Green
} else {
    Write-Host "Warning: Service may not have started correctly" -ForegroundColor Yellow
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nMonitoring Service Commands:"
Write-Host "- Check status: .\Setup-MonitoringService.ps1 -Status"
Write-Host "- Stop service: .\Setup-MonitoringService.ps1 -Stop"
Write-Host "- Start service: .\Setup-MonitoringService.ps1 -Start"
Write-Host "- Remove service: .\Setup-MonitoringService.ps1 -Remove"
Write-Host "`nLogs location: ..\logs\monitoring\"
Write-Host "Metrics location: ..\logs\monitoring\metrics_*.jsonl"
Write-Host "Alerts location: ..\logs\monitoring\alerts.json"