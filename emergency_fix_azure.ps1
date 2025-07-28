# Emergency Azure Fix - Get Site Online NOW
Write-Host "EMERGENCY AZURE FIX - Getting site online" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Red

$resourceGroup = "FoodXchange"
$appName = "foodxchang-2ad3c0f8"

# Step 1: Set the simplest possible startup
Write-Host "`n1. Setting minimal startup command..." -ForegroundColor Yellow
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --startup-file "python -m http.server 8000"

# Step 2: Ensure Python is configured
Write-Host "`n2. Configuring Python runtime..." -ForegroundColor Yellow
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --linux-fx-version "PYTHON|3.12"

# Step 3: Set critical app settings
Write-Host "`n3. Setting app settings..." -ForegroundColor Yellow
az webapp config appsettings set `
    --resource-group $resourceGroup `
    --name $appName `
    --settings `
    WEBSITES_PORT=8000 `
    SCM_DO_BUILD_DURING_DEPLOYMENT=false `
    WEBSITE_RUN_FROM_PACKAGE=0

# Step 4: Deploy minimal files
Write-Host "`n4. Creating minimal deployment..." -ForegroundColor Yellow

# Create index.html
@'
<!DOCTYPE html>
<html>
<head>
    <title>FoodXchange</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
        h1 { color: #ff6b35; }
        .status { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FoodXchange</h1>
        <div class="status">
            <p><strong>System Status:</strong> Maintenance Mode</p>
            <p>We're performing system updates. The platform will be back online shortly.</p>
            <p>Thank you for your patience!</p>
        </div>
        <p>For urgent inquiries, please contact support.</p>
    </div>
</body>
</html>
'@ | Out-File -FilePath "index.html" -Encoding UTF8

# Create minimal zip
if (Test-Path "minimal_fix.zip") { Remove-Item "minimal_fix.zip" }
Compress-Archive -Path "index.html" -DestinationPath "minimal_fix.zip"

# Deploy
Write-Host "`n5. Deploying minimal package..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group $resourceGroup `
    --name $appName `
    --src "minimal_fix.zip"

# Step 5: Restart
Write-Host "`n6. Restarting app service..." -ForegroundColor Yellow
az webapp restart --resource-group $resourceGroup --name $appName

# Step 6: Then update to use app.py
Write-Host "`n7. Waiting 30 seconds then switching to app.py..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --startup-file "python app.py"

# Final restart
az webapp restart --resource-group $resourceGroup --name $appName

Write-Host "`n✅ EMERGENCY FIX APPLIED!" -ForegroundColor Green
Write-Host "The site should be accessible within 2-3 minutes at https://www.fdx.trading" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Check https://www.fdx.trading" -ForegroundColor Cyan
Write-Host "2. Monitor Azure Portal > App Service > Log stream" -ForegroundColor Cyan
Write-Host "3. Once stable, deploy the full application" -ForegroundColor Cyan