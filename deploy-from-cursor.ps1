# Fast deployment script for Cursor IDE terminal
# Run this from Cursor terminal: .\deploy-from-cursor.ps1

Write-Host "🚀 Deploying from Cursor IDE..." -ForegroundColor Cyan

# Create a minimal deployment package
$files = @("index.py", "web.config", "requirements.txt", "app.py")
$existingFiles = $files | Where-Object { Test-Path $_ }

Write-Host "📦 Creating deployment package with: $($existingFiles -join ', ')" -ForegroundColor Yellow

# Create zip file
Compress-Archive -Path $existingFiles -DestinationPath deploy.zip -Force

# Deploy to Azure
Write-Host "☁️ Uploading to Azure..." -ForegroundColor Cyan
$result = az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path deploy.zip --type zip --restart true 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔍 Testing your site..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    # Test the site
    $response = Invoke-WebRequest -Uri "https://www.fdx.trading/health/advanced" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Site is working!" -ForegroundColor Green
        Write-Host "🌐 Visit: https://www.fdx.trading" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  Site is starting up..." -ForegroundColor Yellow
        Write-Host "   Check in 30 seconds at: https://www.fdx.trading" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
}

# Cleanup
Remove-Item deploy.zip -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "💡 Tip: For instant updates, use Kudu console:" -ForegroundColor Magenta
Write-Host "   https://foodxchange-app.scm.azurewebsites.net/DebugConsole" -ForegroundColor Gray