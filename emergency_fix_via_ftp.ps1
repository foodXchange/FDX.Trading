# Emergency FTP deployment fix
Write-Host "Getting FTP deployment credentials..." -ForegroundColor Yellow

$creds = az webapp deployment list-publishing-profiles `
    --name foodxchange-app `
    --resource-group foodxchange-rg `
    --query "[?publishMethod=='FTP'].{url:publishUrl, user:userName, pass:userPWD}[0]" `
    -o json | ConvertFrom-Json

if ($creds) {
    Write-Host "FTP URL: $($creds.url)" -ForegroundColor Green
    Write-Host "Username: $($creds.user)" -ForegroundColor Green
    Write-Host "Password: [Hidden]" -ForegroundColor Green
    
    Write-Host "`nTo fix via FTP:" -ForegroundColor Yellow
    Write-Host "1. Use an FTP client (like FileZilla)"
    Write-Host "2. Connect to: $($creds.url)"
    Write-Host "3. Navigate to: /site/wwwroot"
    Write-Host "4. Delete all files"
    Write-Host "5. Upload the minimal app files"
} else {
    Write-Host "Could not retrieve FTP credentials" -ForegroundColor Red
}

# Alternative: Use deployment center
Write-Host "`nAlternative - Reset via Portal:" -ForegroundColor Yellow
Write-Host "1. Go to Azure Portal"
Write-Host "2. Navigate to your web app"
Write-Host "3. Go to Deployment Center"
Write-Host "4. Disconnect current source"
Write-Host "5. Set up Local Git deployment"
Write-Host "6. Push minimal app via git"