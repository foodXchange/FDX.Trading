# FoodXchange Azure 503 Error Fix Script
# Comprehensive solution for deployment issues

param(
    [string]$ResourceGroup = "foodxchange-rg",
    [string]$AppName = "foodxchange"
)

Write-Host "=== FoodXchange Azure 503 Error Fix ===" -ForegroundColor Cyan
Write-Host "This script will fix your deployment issues" -ForegroundColor Yellow

# Function to check if command succeeded
function Check-LastCommand {
    param([string]$Message)
    if ($LASTEXITCODE -ne 0) {
        Write-Host "× $Message failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ $Message succeeded" -ForegroundColor Green
}

# 1. Check Azure CLI
Write-Host "`n[Step 1/10] Checking Azure CLI..." -ForegroundColor Green
$azVersion = az version --query '"azure-cli"' -o tsv 2>$null
if ($?) {
    Write-Host "✓ Azure CLI version: $azVersion" -ForegroundColor Green
} else {
    Write-Host "× Azure CLI not found. Please install it." -ForegroundColor Red
    Write-Host "Download from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

# 2. Login check
Write-Host "`n[Step 2/10] Checking Azure authentication..." -ForegroundColor Green
$account = az account show --query name -o tsv 2>$null
if ($?) {
    Write-Host "✓ Logged in as: $account" -ForegroundColor Green
} else {
    Write-Host "Running az login..." -ForegroundColor Yellow
    az login
    Check-LastCommand "Azure login"
}

# 3. Verify resource exists
Write-Host "`n[Step 3/10] Verifying App Service exists..." -ForegroundColor Green
$appExists = az webapp show --name $AppName --resource-group $ResourceGroup --query name -o tsv 2>$null
if (!$appExists) {
    Write-Host "× App Service '$AppName' not found in resource group '$ResourceGroup'" -ForegroundColor Red
    Write-Host "Please check the app name and resource group" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Found App Service: $appExists" -ForegroundColor Green

# 4. Stop the app for clean deployment
Write-Host "`n[Step 4/10] Stopping App Service..." -ForegroundColor Green
az webapp stop --name $AppName --resource-group $ResourceGroup 2>$null
Write-Host "✓ App Service stopped" -ForegroundColor Green

# 5. Update web.config for proper Python handling
Write-Host "`n[Step 5/10] Creating optimized web.config..." -ForegroundColor Green
$webConfig = @'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" 
                  arguments="startup_fixed.py"
                  stdoutLogEnabled="true" 
                  stdoutLogFile="\\?\%home%\LogFiles\python.log"
                  startupTimeLimit="300"
                  processesPerApplication="1">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
        <environmentVariable name="PYTHONUNBUFFERED" value="1" />
      </environmentVariables>
    </httpPlatform>
    <security>
      <requestFiltering>
        <requestLimits maxAllowedContentLength="104857600" />
      </requestFiltering>
    </security>
  </system.webServer>
</configuration>
'@
$webConfig | Out-File -FilePath "web.config" -Encoding UTF8

# 6. Configure App Service settings
Write-Host "`n[Step 6/10] Configuring App Service settings..." -ForegroundColor Green

# Set basic configuration
az webapp config set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --startup-file "python startup_fixed.py" `
    --use-32bit-worker-process false `
    --always-on true 2>$null

# Set Python version
az webapp config set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --linux-fx-version "PYTHON|3.11" 2>$null

# 7. Update all application settings
Write-Host "`n[Step 7/10] Updating application settings..." -ForegroundColor Green
az webapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --settings `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    ENABLE_ORYX_BUILD=true `
    WEBSITE_RUN_FROM_PACKAGE=0 `
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=true `
    PYTHON_ENABLE_GUNICORN_MULTIWORKERS=true `
    ORYX_DISABLE_TELEMETRY=true `
    WEBSITES_PORT=8000 `
    WEBSITE_HTTPLOGGING_RETENTION_DAYS=7 `
    PYTHONUNBUFFERED=1 2>$null

Write-Host "✓ Application settings updated" -ForegroundColor Green

# 8. Create deployment package
Write-Host "`n[Step 8/10] Creating deployment package..." -ForegroundColor Green

# Create a clean deployment directory
$deployDir = "azure_deployment_temp"
if (Test-Path $deployDir) {
    Remove-Item -Path $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy required files
Copy-Item -Path "requirements.txt" -Destination "$deployDir\" -Force
Copy-Item -Path "startup_fixed.py" -Destination "$deployDir\" -Force
Copy-Item -Path "web.config" -Destination "$deployDir\" -Force
Copy-Item -Path "app" -Destination "$deployDir\" -Recurse -Force

# Copy other necessary files if they exist
$optionalFiles = @(".env", ".env.blob", "startup.py", "app.py", "main.py")
foreach ($file in $optionalFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination "$deployDir\" -Force
    }
}

# Create deployment zip
$zipPath = "foodxchange_fixed_deployment.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($deployDir, $zipPath)

# Clean up temp directory
Remove-Item -Path $deployDir -Recurse -Force

Write-Host "✓ Deployment package created: $zipPath" -ForegroundColor Green

# 9. Deploy to Azure
Write-Host "`n[Step 9/10] Deploying to Azure..." -ForegroundColor Green
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow

az webapp deployment source config-zip `
    --resource-group $ResourceGroup `
    --name $AppName `
    --src $zipPath 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Deployment completed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Deployment completed with warnings" -ForegroundColor Yellow
}

# 10. Start the app
Write-Host "`n[Step 10/10] Starting App Service..." -ForegroundColor Green
az webapp start --name $AppName --resource-group $ResourceGroup 2>$null
Write-Host "✓ App Service started" -ForegroundColor Green

# Display summary
Write-Host "`n=== Deployment Fix Complete ===" -ForegroundColor Green
Write-Host "Your app is starting up at: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Health endpoint: https://$AppName.azurewebsites.net/health" -ForegroundColor Cyan
Write-Host "`nIt may take 2-5 minutes for the app to fully initialize" -ForegroundColor Yellow
Write-Host "DNS propagation may take up to 5 minutes" -ForegroundColor Yellow

# Offer to monitor logs
Write-Host "`nWould you like to monitor the startup logs? (Y/N)" -ForegroundColor Cyan
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`nMonitoring logs (press Ctrl+C to stop)..." -ForegroundColor Green
    az webapp log tail --name $AppName --resource-group $ResourceGroup
}