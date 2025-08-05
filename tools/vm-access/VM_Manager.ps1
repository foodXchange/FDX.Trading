# FDX VM Manager - PowerShell Edition
# Advanced VM Management Tools

$VMHost = "4.206.1.15"
$VMUser = "fdxfounder"
$SSHKey = "$env:USERPROFILE\.ssh\fdx_founders_key"

function Show-Menu {
    Clear-Host
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "         FDX VM MANAGER (PowerShell)        " -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "VM Status:" -NoNewline
    
    # Test VM connectivity
    if (Test-Connection -ComputerName $VMHost -Count 1 -Quiet) {
        Write-Host " ONLINE" -ForegroundColor Green
    } else {
        Write-Host " OFFLINE" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "[1] Quick SSH Command" -ForegroundColor Yellow
    Write-Host "[2] Upload Files to VM" -ForegroundColor Yellow
    Write-Host "[3] Download Files from VM" -ForegroundColor Yellow
    Write-Host "[4] View VM Logs" -ForegroundColor Yellow
    Write-Host "[5] Restart Services" -ForegroundColor Yellow
    Write-Host "[6] Port Forwarding Setup" -ForegroundColor Yellow
    Write-Host "[7] Backup Database" -ForegroundColor Yellow
    Write-Host "[8] System Health Check" -ForegroundColor Yellow
    Write-Host "[9] Open All Services" -ForegroundColor Yellow
    Write-Host "[0] Return to Main Menu" -ForegroundColor Yellow
    Write-Host ""
}

function Execute-SSHCommand {
    param($Command)
    ssh -i $SSHKey "$VMUser@$VMHost" $Command
}

function Quick-SSH {
    $cmd = Read-Host "Enter command to run on VM"
    Write-Host "Executing: $cmd" -ForegroundColor Cyan
    Execute-SSHCommand $cmd
    Read-Host "Press Enter to continue"
}

function Upload-Files {
    $source = Read-Host "Enter local file/folder path"
    $dest = Read-Host "Enter VM destination path (default: /home/fdxfounder/)"
    if ([string]::IsNullOrEmpty($dest)) { $dest = "/home/fdxfounder/" }
    
    Write-Host "Uploading $source to $dest..." -ForegroundColor Cyan
    scp -i $SSHKey -r $source "${VMUser}@${VMHost}:${dest}"
    Write-Host "Upload complete!" -ForegroundColor Green
    Read-Host "Press Enter to continue"
}

function Download-Files {
    $source = Read-Host "Enter VM file/folder path"
    $dest = Read-Host "Enter local destination (default: current directory)"
    if ([string]::IsNullOrEmpty($dest)) { $dest = "." }
    
    Write-Host "Downloading $source to $dest..." -ForegroundColor Cyan
    scp -i $SSHKey -r "${VMUser}@${VMHost}:${source}" $dest
    Write-Host "Download complete!" -ForegroundColor Green
    Read-Host "Press Enter to continue"
}

function View-Logs {
    Write-Host "Select log to view:" -ForegroundColor Yellow
    Write-Host "[1] FoodXchange App"
    Write-Host "[2] FDX Crawler"
    Write-Host "[3] Nginx"
    Write-Host "[4] System"
    
    $choice = Read-Host "Select option"
    $lines = Read-Host "Number of lines (default: 50)"
    if ([string]::IsNullOrEmpty($lines)) { $lines = "50" }
    
    switch ($choice) {
        "1" { Execute-SSHCommand "sudo journalctl -u foodxchange -n $lines --no-pager" }
        "2" { Execute-SSHCommand "sudo journalctl -u fdx-crawler -n $lines --no-pager" }
        "3" { Execute-SSHCommand "sudo tail -n $lines /var/log/nginx/error.log" }
        "4" { Execute-SSHCommand "sudo journalctl -n $lines --no-pager" }
    }
    Read-Host "Press Enter to continue"
}

function Restart-Services {
    Write-Host "Select service to restart:" -ForegroundColor Yellow
    Write-Host "[1] FoodXchange App"
    Write-Host "[2] FDX Crawler"
    Write-Host "[3] Nginx"
    Write-Host "[4] PostgreSQL"
    
    $choice = Read-Host "Select option"
    
    switch ($choice) {
        "1" { Execute-SSHCommand "sudo systemctl restart foodxchange" }
        "2" { Execute-SSHCommand "sudo systemctl restart fdx-crawler" }
        "3" { Execute-SSHCommand "sudo systemctl restart nginx" }
        "4" { Execute-SSHCommand "sudo systemctl restart postgresql" }
    }
    Write-Host "Service restarted!" -ForegroundColor Green
    Read-Host "Press Enter to continue"
}

function Setup-PortForwarding {
    Write-Host "Setting up port forwarding..." -ForegroundColor Cyan
    Write-Host "This will open monitoring tools locally" -ForegroundColor Yellow
    
    # Kill existing SSH tunnels
    Get-Process ssh -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*3000*" -or $_.CommandLine -like "*19999*"} | Stop-Process -Force
    
    # Create new tunnels
    Start-Process ssh -ArgumentList "-i $SSHKey -L 3000:localhost:3000 -L 19999:localhost:19999 -N $VMUser@$VMHost" -WindowStyle Hidden
    
    Start-Sleep -Seconds 2
    Write-Host "Port forwarding active!" -ForegroundColor Green
    Write-Host "Grafana: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Netdata: http://localhost:19999" -ForegroundColor Cyan
    Read-Host "Press Enter to continue"
}

function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Write-Host "Creating database backup..." -ForegroundColor Cyan
    
    Execute-SSHCommand "pg_dump -U fdxfounder -d foodxchange | gzip > ~/backups/fdx_backup_$timestamp.sql.gz"
    
    $download = Read-Host "Download backup locally? (Y/N)"
    if ($download -eq "Y") {
        scp -i $SSHKey "${VMUser}@${VMHost}:~/backups/fdx_backup_$timestamp.sql.gz" "."
        Write-Host "Backup downloaded to current directory!" -ForegroundColor Green
    }
    Read-Host "Press Enter to continue"
}

function System-HealthCheck {
    Write-Host "Running system health check..." -ForegroundColor Cyan
    Execute-SSHCommand @"
echo '=== System Health Check ==='
echo 'CPU Usage:' && top -bn1 | grep 'Cpu(s)' | awk '{print \$2}'
echo ''
echo 'Memory Usage:' && free -h
echo ''
echo 'Disk Usage:' && df -h
echo ''
echo 'Service Status:'
systemctl is-active foodxchange nginx postgresql fdx-crawler
echo ''
echo 'Last 5 system errors:'
sudo journalctl -p err -n 5 --no-pager
"@
    Read-Host "Press Enter to continue"
}

function Open-AllServices {
    Write-Host "Opening all services..." -ForegroundColor Cyan
    
    # Setup port forwarding first
    Get-Process ssh -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*3000*" -or $_.CommandLine -like "*19999*"} | Stop-Process -Force
    Start-Process ssh -ArgumentList "-i $SSHKey -L 3000:localhost:3000 -L 19999:localhost:19999 -N $VMUser@$VMHost" -WindowStyle Hidden
    
    Start-Sleep -Seconds 2
    
    # Open all services
    Start-Process "http://4.206.1.15"
    Start-Process "http://4.206.1.15:8003"
    Start-Process "http://localhost:3000"
    Start-Process "http://localhost:19999"
    
    Write-Host "All services opened!" -ForegroundColor Green
    Read-Host "Press Enter to continue"
}

# Main loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Select option"
    
    switch ($choice) {
        "1" { Quick-SSH }
        "2" { Upload-Files }
        "3" { Download-Files }
        "4" { View-Logs }
        "5" { Restart-Services }
        "6" { Setup-PortForwarding }
        "7" { Backup-Database }
        "8" { System-HealthCheck }
        "9" { Open-AllServices }
        "0" { exit }
        default { Write-Host "Invalid option" -ForegroundColor Red; Start-Sleep -Seconds 2 }
    }
}