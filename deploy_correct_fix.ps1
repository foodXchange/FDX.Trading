# Deploy the correct health endpoint fix
$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"

Write-Host "Deploying correct health endpoint fix..." -ForegroundColor Green

# Create a zip package with the minimal app
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path "app_minimal.py" -DestinationPath "minimal_deploy.zip" -Force

# Deploy the package
Write-Host "Deploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group $resourceGroup `
    --name $appName `
    --src "minimal_deploy.zip"

# Update startup command to use the minimal app
Write-Host "Setting startup command..." -ForegroundColor Yellow
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app_minimal:application"

# Create minimal requirements
Write-Host "Creating minimal requirements..." -ForegroundColor Yellow
"gunicorn==21.2.0" | Out-File -FilePath "requirements_minimal.txt" -Encoding utf8

# Upload requirements
az webapp deploy `
    --resource-group $resourceGroup `
    --name $appName `
    --src-path "requirements_minimal.txt" `
    --type static `
    --target-path "/home/site/wwwroot/requirements.txt"

# Restart app
Write-Host "Restarting app..." -ForegroundColor Yellow
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Testing health endpoint..." -ForegroundColor Cyan

# Wait a moment for restart
Start-Sleep -Seconds 10

# Test the endpoint
$response = Invoke-RestMethod -Uri "https://foodxchange-app.azurewebsites.net/health/simple" -Method Get
Write-Host "Health endpoint response: $response" -ForegroundColor Green