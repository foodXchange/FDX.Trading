# Minimal deployment script
Write-Host "Creating minimal deployment package..." -ForegroundColor Yellow

# Create a minimal requirements file
@"
fastapi==0.111.0
uvicorn[standard]==0.30.1
"@ | Set-Content requirements_minimal.txt

# Create deployment zip with only essential files
Compress-Archive -Path @(
    "minimal_app.py",
    "requirements_minimal.txt",
    "startup.sh",
    "web.config",
    "runtime.txt"
) -DestinationPath minimal_deploy.zip -Force

Write-Host "Deploying minimal app to Azure..." -ForegroundColor Yellow
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path minimal_deploy.zip --type zip

Write-Host "Checking deployment status..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test the endpoint
Write-Host "Testing endpoint..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "https://foodxchange-app.azurewebsites.net/health" -UseBasicParsing -TimeoutSec 10
Write-Host "Response: $($response.StatusCode)" -ForegroundColor Green
Write-Host $response.Content