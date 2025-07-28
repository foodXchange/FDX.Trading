# Direct Azure deployment without GitHub
Write-Host "Direct Azure Deployment" -ForegroundColor Green

$resourceGroup = "FoodXchange"
$appName = "foodxchang-2ad3c0f8"

# Create a working deployment package
Write-Host "Creating deployment package..." -ForegroundColor Yellow

# Ensure prebuild.sh exists
if (!(Test-Path "prebuild.sh")) {
    "#!/bin/bash`necho 'Prebuild running...'" | Out-File -FilePath "prebuild.sh" -Encoding ASCII
}

# Create a minimal but working package
$files = @(
    "app.py",
    "requirements.txt",
    "startup.py",
    "startup_robust.py",
    "prebuild.sh",
    "web.config"
)

# Add app directory
if (Test-Path "app") {
    $files += "app"
}

# Remove old package
if (Test-Path "direct_deploy.zip") {
    Remove-Item "direct_deploy.zip"
}

# Create package
foreach ($file in $files) {
    if (Test-Path $file) {
        Compress-Archive -Path $file -Update -DestinationPath "direct_deploy.zip"
    }
}

Write-Host "Deploying package..." -ForegroundColor Yellow

# Deploy
az webapp deployment source config-zip `
    --resource-group $resourceGroup `
    --name $appName `
    --src "direct_deploy.zip"

# Set startup command
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --startup-file "python startup.py"

# Restart
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Check https://www.fdx.trading in 2-3 minutes" -ForegroundColor Cyan