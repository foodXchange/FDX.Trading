# Quick Azure Deployment Fix PowerShell Script
Write-Host "Quick Azure Deployment Fix" -ForegroundColor Cyan
Write-Host ("=" * 50)

# Check if Azure CLI is installed
try {
    $azVersion = az --version
    Write-Host "[OK] Azure CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Azure CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Deploy the package
Write-Host "`nDeploying to Azure..." -ForegroundColor Yellow
Write-Host "This will take 2-3 minutes..."

$result = az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path azure_quick_fix.zip --type zip --restart true 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Deployment successful!" -ForegroundColor Green
    
    # Set startup command
    Write-Host "`nSetting startup command..." -ForegroundColor Yellow
    az webapp config set --name foodxchange-app --resource-group foodxchange-rg --startup-file "python -m uvicorn app:app --host 0.0.0.0 --port 8000" | Out-Null
    
    # Restart app
    Write-Host "Restarting app..." -ForegroundColor Yellow
    az webapp restart --name foodxchange-app --resource-group foodxchange-rg | Out-Null
    
    Write-Host "`nWaiting for app to start (60 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
    
    # Test the app
    Write-Host "`nTesting deployment..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "https://foodxchange-app.azurewebsites.net/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "[SUCCESS] App is working!" -ForegroundColor Green
            Write-Host "Response: $($response.Content)" -ForegroundColor Gray
        } else {
            Write-Host "[WARNING] App returned status $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[ERROR] Test failed: $_" -ForegroundColor Red
    }
    
    Write-Host "`nDeployment Summary:" -ForegroundColor Cyan
    Write-Host "- URL: https://foodxchange-app.azurewebsites.net" -ForegroundColor White
    Write-Host "- Health: https://foodxchange-app.azurewebsites.net/health" -ForegroundColor White
    Write-Host "- Kudu: https://foodxchange-app.scm.azurewebsites.net" -ForegroundColor White
    
} else {
    Write-Host "[ERROR] Deployment failed!" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
    
    Write-Host "`nTrying alternative deployment method..." -ForegroundColor Yellow
    $result2 = az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange-app --src azure_quick_fix.zip 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Alternative deployment successful!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Alternative deployment also failed" -ForegroundColor Red
        Write-Host $result2 -ForegroundColor Red
    }
}