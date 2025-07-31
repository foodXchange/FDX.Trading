# FoodXchange Daily Task Setup PowerShell Script
# Requires administrator privileges

param(
    [switch]$Remove,
    [switch]$Test,
    [string]$Time = "02:00"
)

$ErrorActionPreference = "Stop"

# Check for admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script requires Administrator privileges. Please run as Administrator."
    exit 1
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  FoodXchange Daily Task Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$scriptPath = $PSScriptRoot
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $pythonPath) {
    $pythonPath = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe"
    if (-not (Test-Path $pythonPath)) {
        Write-Error "Python not found. Please ensure Python is installed and in PATH."
        exit 1
    }
}

# Task definitions
$tasks = @(
    @{
        Name = "FoodXchange_Daily_Maintenance"
        Description = "Performs daily maintenance tasks including cache cleanup, backups, and health checks"
        Script = Join-Path $scriptPath "daily_maintenance.py"
        Schedule = "Daily"
        Time = $Time
        Priority = "High"
    },
    @{
        Name = "FoodXchange_Redis_Monitor"
        Description = "Monitors Redis performance and collects metrics"
        Script = Join-Path $scriptPath "redis_monitor.py"
        Schedule = "Hourly"
        Interval = 1
        Priority = "Normal"
    },
    @{
        Name = "FoodXchange_Cache_Optimizer"
        Description = "Optimizes Redis cache performance"
        Script = Join-Path $scriptPath "redis_cache_manager.py"
        Schedule = "Daily"
        Time = "05:00"
        Priority = "Normal"
    },
    @{
        Name = "FoodXchange_Weekly_Backup"
        Description = "Creates comprehensive system backup"
        Script = Join-Path (Split-Path $scriptPath) "fx.bat"
        Arguments = "backup"
        Schedule = "Weekly"
        DayOfWeek = "Sunday"
        Time = "03:00"
        Priority = "High"
    }
)

if ($Remove) {
    Write-Host "`nRemoving scheduled tasks..." -ForegroundColor Yellow
    foreach ($task in $tasks) {
        try {
            Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false -ErrorAction SilentlyContinue
            Write-Host "[REMOVED] $($task.Name)" -ForegroundColor Green
        } catch {
            Write-Host "[SKIPPED] $($task.Name) - Not found" -ForegroundColor Gray
        }
    }
    exit 0
}

if ($Test) {
    Write-Host "`nTesting task scripts..." -ForegroundColor Yellow
    foreach ($task in $tasks) {
        if ($task.Script -like "*.py") {
            Write-Host "`nTesting: $($task.Name)" -ForegroundColor Cyan
            try {
                $process = Start-Process -FilePath $pythonPath -ArgumentList $task.Script -NoNewWindow -PassThru -Wait
                if ($process.ExitCode -eq 0) {
                    Write-Host "[OK] Script executed successfully" -ForegroundColor Green
                } else {
                    Write-Host "[ERROR] Script failed with exit code: $($process.ExitCode)" -ForegroundColor Red
                }
            } catch {
                Write-Host "[ERROR] Failed to run script: $_" -ForegroundColor Red
            }
        }
    }
    exit 0
}

# Create scheduled tasks
Write-Host "`nCreating scheduled tasks..." -ForegroundColor Yellow

foreach ($task in $tasks) {
    try {
        # Remove existing task
        Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false -ErrorAction SilentlyContinue
        
        # Build action
        if ($task.Script -like "*.py") {
            $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$($task.Script)`""
        } else {
            $args = if ($task.Arguments) { $task.Arguments } else { "" }
            $action = New-ScheduledTaskAction -Execute $task.Script -Argument $args
        }
        
        # Build trigger based on schedule type
        switch ($task.Schedule) {
            "Daily" {
                $trigger = New-ScheduledTaskTrigger -Daily -At $task.Time
            }
            "Hourly" {
                $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours $task.Interval) -RepetitionDuration (New-TimeSpan -Days 365)
            }
            "Weekly" {
                $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $task.DayOfWeek -At $task.Time
            }
        }
        
        # Set principal (run with highest privileges)
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        # Set settings
        $settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -RestartCount 3 `
            -RestartInterval (New-TimeSpan -Minutes 1) `
            -ExecutionTimeLimit (New-TimeSpan -Hours 2)
        
        # Register task
        Register-ScheduledTask `
            -TaskName $task.Name `
            -Description $task.Description `
            -Action $action `
            -Trigger $trigger `
            -Principal $principal `
            -Settings $settings `
            -Force | Out-Null
        
        Write-Host "[CREATED] $($task.Name)" -ForegroundColor Green
        Write-Host "          Schedule: $($task.Schedule) $(if ($task.Time) { "at $($task.Time)" })" -ForegroundColor Gray
        
    } catch {
        Write-Host "[FAILED] $($task.Name) - $_" -ForegroundColor Red
    }
}

# Create event log source for FoodXchange if it doesn't exist
try {
    if (-not [System.Diagnostics.EventLog]::SourceExists("FoodXchange")) {
        [System.Diagnostics.EventLog]::CreateEventSource("FoodXchange", "Application")
        Write-Host "`n[CREATED] Windows Event Log source 'FoodXchange'" -ForegroundColor Green
    }
} catch {
    Write-Host "`n[WARNING] Could not create Event Log source" -ForegroundColor Yellow
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nScheduled Tasks Created:"
Write-Host "- Daily Maintenance (2:00 AM)"
Write-Host "- Redis Monitoring (Every hour)"
Write-Host "- Cache Optimization (5:00 AM daily)"
Write-Host "- Weekly Backup (Sundays 3:00 AM)"
Write-Host "`nManagement Commands:"
Write-Host "- View tasks: Get-ScheduledTask -TaskName 'FoodXchange_*'"
Write-Host "- Test tasks: .\Setup-DailyTasks.ps1 -Test"
Write-Host "- Remove tasks: .\Setup-DailyTasks.ps1 -Remove"
Write-Host "- Run a task now: Start-ScheduledTask -TaskName 'FoodXchange_Daily_Maintenance'"