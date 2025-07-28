# Deploy minimal working app to Azure
$resourceGroup = "FoodXchange"
$appName = "FoodXchange-app"

Write-Host "Deploying minimal fix to Azure..." -ForegroundColor Green

# Set startup command
Write-Host "Setting startup command..." -ForegroundColor Yellow
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app_minimal:application"

# Deploy just the minimal app file
Write-Host "Deploying app_minimal.py..." -ForegroundColor Yellow
az webapp deploy `
    --resource-group $resourceGroup `
    --name $appName `
    --src-path "app_minimal.py" `
    --type static `
    --target-path "/home/site/wwwroot/app_minimal.py"

# Update requirements to minimal
Write-Host "Creating minimal requirements..." -ForegroundColor Yellow
"gunicorn==21.2.0" | Out-File -FilePath "requirements_azure.txt" -Encoding utf8

az webapp deploy `
    --resource-group $resourceGroup `
    --name $appName `
    --src-path "requirements_azure.txt" `
    --type static `
    --target-path "/home/site/wwwroot/requirements.txt"

# Restart the app
Write-Host "Restarting app..." -ForegroundColor Yellow
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Check: https://foodxchange-app.azurewebsites.net/health/simple" -ForegroundColor Cyan