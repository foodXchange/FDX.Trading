# FoodXchange VM Quick Access Script
# Run this script to quickly access your VM and webapps

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    FoodXchange VM Quick Access" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Show-Menu {
    Write-Host "Choose an option:" -ForegroundColor Yellow
    Write-Host "1. SSH to VM" -ForegroundColor White
    Write-Host "2. Open FastAPI App" -ForegroundColor White
    Write-Host "3. Open Grafana Monitoring" -ForegroundColor White
    Write-Host "4. Open Netdata Real-time" -ForegroundColor White
    Write-Host "5. Open Quick Access Dashboard" -ForegroundColor White
    Write-Host "6. Check VM Status" -ForegroundColor White
    Write-Host "7. Open Cursor with VM" -ForegroundColor White
    Write-Host "8. Exit" -ForegroundColor White
    Write-Host ""
}

function Connect-SSH {
    Write-Host "Connecting to VM via SSH..." -ForegroundColor Green
    ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
}

function Open-WebApp {
    param([string]$Url, [string]$Name)
    Write-Host "Opening $Name..." -ForegroundColor Green
    Start-Process $Url
}

function Check-VMStatus {
    Write-Host "Checking VM status..." -ForegroundColor Green
    try {
        $result = ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15 "echo 'VM is running' && uptime" 2>$null
        if ($result) {
            Write-Host "✅ VM is running and accessible" -ForegroundColor Green
            Write-Host "System uptime: $result" -ForegroundColor Cyan
            
            # Check web applications
            Write-Host "`n🌐 Checking Web Applications:" -ForegroundColor Yellow
            $fastapi = ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15 "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000" 2>$null
            $grafana = ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15 "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000" 2>$null
            $netdata = ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15 "curl -s -o /dev/null -w '%{http_code}' http://localhost:19999" 2>$null
            
            if ($fastapi -eq "200") { Write-Host "✅ FastAPI App (FDX.trading): Running" -ForegroundColor Green }
            else { Write-Host "❌ FastAPI App: Not responding" -ForegroundColor Red }
            
            if ($grafana -eq "302") { Write-Host "✅ Grafana Monitoring: Running" -ForegroundColor Green }
            else { Write-Host "❌ Grafana: Not responding" -ForegroundColor Red }
            
            if ($netdata -eq "200") { Write-Host "✅ Netdata Real-time: Running" -ForegroundColor Green }
            else { Write-Host "❌ Netdata: Not responding" -ForegroundColor Red }
        }
    }
    catch {
        Write-Host "❌ VM is not accessible" -ForegroundColor Red
    }
}

function Open-CursorVM {
    Write-Host "Opening Cursor for VM connection..." -ForegroundColor Green
    cursor
    Write-Host "In Cursor, press Ctrl+Shift+P and type: Remote-SSH: Connect to Host" -ForegroundColor Yellow
    Write-Host "Then enter: fdxfounder@4.206.1.15" -ForegroundColor Yellow
}

do {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-8)"
    
    switch ($choice) {
        "1" { Connect-SSH }
        "2" { Open-WebApp "http://4.206.1.15" "FastAPI App" }
        "3" { Open-WebApp "http://4.206.1.15:3000" "Grafana Monitoring" }
        "4" { Open-WebApp "http://4.206.1.15:19999" "Netdata Real-time" }
        "5" { 
            if (Test-Path "quick_vm_access.html") {
                Open-WebApp "quick_vm_access.html" "Quick Access Dashboard"
            } else {
                Write-Host "Quick access dashboard not found. Opening webapps directly..." -ForegroundColor Yellow
                Open-WebApp "http://4.206.1.15" "FastAPI App"
            }
        }
        "6" { Check-VMStatus }
        "7" { Open-CursorVM }
        "8" { 
            Write-Host "Goodbye!" -ForegroundColor Green
            exit 
        }
        default { 
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
        }
    }
    
    if ($choice -ne "8") {
        Write-Host ""
        Read-Host "Press Enter to continue"
        Clear-Host
    }
} while ($choice -ne "8") 