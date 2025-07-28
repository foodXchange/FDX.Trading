# Fast deployment script for FoodXchange
# Deploys directly to Azure in 30-60 seconds

Write-Host "🚀 Deploying to Azure..." -ForegroundColor Cyan

# Deploy only essential files
az webapp deploy `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --src-path . `
    --type zip `
    --clean true `
    --restart true

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host "🌐 Your app is at: https://www.fdx.trading" -ForegroundColor Yellow
    
    # Test the health endpoint
    Start-Sleep -Seconds 5
    $response = Invoke-WebRequest -Uri "https://www.fdx.trading/health/advanced" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Health check passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Health check failed - app may still be starting" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
}