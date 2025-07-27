# Set Azure App Service Environment Variables
Write-Host "=== Setting Azure App Service Environment Variables ===" -ForegroundColor Cyan

$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"

# Load environment variables from .env files
Write-Host "Loading environment variables from local .env files..." -ForegroundColor Yellow

# Read .env file
$envVars = @{}
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$key] = $value
        }
    }
}

# Read .env.blob file for Azure storage
if (Test-Path ".env.blob") {
    Get-Content ".env.blob" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$key] = $value
        }
    }
}

# Critical variables to set
$criticalVars = @(
    "DATABASE_URL",
    "SECRET_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
    "AZURE_STORAGE_CONNECTION_STRING"
)

Write-Host "`nSetting critical environment variables..." -ForegroundColor Yellow
$settings = @()

foreach ($var in $criticalVars) {
    if ($envVars.ContainsKey($var)) {
        $settings += "$var=$($envVars[$var])"
        Write-Host "   [OK] $var will be set" -ForegroundColor Green
    } else {
        Write-Host "   [MISSING] $var not found in .env files!" -ForegroundColor Red
    }
}

# Add additional settings
$settings += "PYTHONPATH=/home/site/wwwroot"
$settings += "PORT=8000"
$settings += "ENVIRONMENT=production"
$settings += "DEBUG=False"

Write-Host "`nApplying settings to Azure..." -ForegroundColor Yellow
az webapp config appsettings set `
    --name $appName `
    --resource-group $resourceGroup `
    --settings $settings

Write-Host "`nEnvironment variables set successfully!" -ForegroundColor Green
Write-Host "Restarting app to apply changes..." -ForegroundColor Yellow

az webapp restart --name $appName --resource-group $resourceGroup

Write-Host "`nDone! Wait 30-60 seconds for the app to restart." -ForegroundColor Cyan
Write-Host "Then check: https://foodxchange-app.azurewebsites.net" -ForegroundColor White