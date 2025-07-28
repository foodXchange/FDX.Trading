# PowerShell script for ultra-fast Azure deployment
# Run: .\quick-deploy.ps1

Write-Host "Quick Deploy to Azure" -ForegroundColor Cyan

# Create deployment package (exclude unnecessary files)
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path @(
    "foodxchange",
    "main.py",
    "requirements.txt",
    "startup.sh",
    "web.config",
    "runtime.txt"
) -DestinationPath deploy.zip -Force

# Deploy to Azure
Write-Host "Deploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group foodxchange-rg `
    --name foodxchange-app `
    --src deploy.zip

# Check deployment status
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Checking app status..." -ForegroundColor Yellow
az webapp show --name foodxchange-app --resource-group foodxchange-rg --query state -o tsv

# Tail logs
Write-Host "Tailing logs (Ctrl+C to stop)..." -ForegroundColor Cyan
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg