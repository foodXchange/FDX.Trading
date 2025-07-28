# Deploy complete FoodXchange app to Azure
Write-Host "Deploying complete FoodXchange app to Azure..." -ForegroundColor Yellow

# Create deployment directory
$deployDir = "foodxchange_complete"
if (Test-Path $deployDir) { Remove-Item $deployDir -Recurse -Force }
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy necessary files
Write-Host "Copying application files..." -ForegroundColor Cyan

# Create app directory structure
New-Item -ItemType Directory -Path "$deployDir\app" | Out-Null
New-Item -ItemType Directory -Path "$deployDir\app\models" | Out-Null
New-Item -ItemType Directory -Path "$deployDir\app\routes" | Out-Null
New-Item -ItemType Directory -Path "$deployDir\app\services" | Out-Null
New-Item -ItemType Directory -Path "$deployDir\app\templates" | Out-Null
New-Item -ItemType Directory -Path "$deployDir\app\static" | Out-Null

# Copy Python files
Copy-Item "app\*.py" "$deployDir\app\" -Force
Copy-Item "app\models\*.py" "$deployDir\app\models\" -Force
Copy-Item "app\routes\*.py" "$deployDir\app\routes\" -Force -ErrorAction SilentlyContinue
Copy-Item "app\services\*.py" "$deployDir\app\services\" -Force -ErrorAction SilentlyContinue
Copy-Item "app\templates\*" "$deployDir\app\templates\" -Force -ErrorAction SilentlyContinue
Copy-Item "app\static\*" "$deployDir\app\static\" -Recurse -Force -ErrorAction SilentlyContinue

# Copy root files
Copy-Item "requirements.txt" "$deployDir\" -Force
Copy-Item "startup_robust.py" "$deployDir\" -Force
Copy-Item ".env*" "$deployDir\" -Force -ErrorAction SilentlyContinue

# Create startup.txt
"python startup_robust.py" | Out-File -FilePath "$deployDir\startup.txt" -Encoding UTF8

# Create web.config
@'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" 
                  arguments="startup_robust.py" 
                  stdoutLogEnabled="true" 
                  stdoutLogFile="\\?\%home%\LogFiles\python.log"
                  startupTimeLimit="300"
                  requestTimeout="00:05:00">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
'@ | Out-File -FilePath "$deployDir\web.config" -Encoding UTF8

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Cyan
$zipPath = "foodxchange_complete.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Compress-Archive -Path "$deployDir\*" -DestinationPath $zipPath -Force

# Deploy to Azure
Write-Host "Deploying to Azure..." -ForegroundColor Green
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path $zipPath --type zip

# Set configuration
Write-Host "Configuring Azure app..." -ForegroundColor Cyan
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "python startup_robust.py"
az webapp config appsettings set --resource-group foodxchange-rg --name foodxchange-app --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true WEBSITE_RUN_FROM_PACKAGE=0

# Restart app
Write-Host "Restarting app..." -ForegroundColor Cyan
az webapp restart --resource-group foodxchange-rg --name foodxchange-app

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Wait 60 seconds for app to start, then check:" -ForegroundColor Yellow
Write-Host "https://www.fdx.trading/health/simple" -ForegroundColor Cyan
Write-Host "https://foodxchange-app.azurewebsites.net/health/simple" -ForegroundColor Cyan

# Clean up
Remove-Item $deployDir -Recurse -Force -ErrorAction SilentlyContinue