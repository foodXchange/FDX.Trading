# Azure Deployment Fix Script
# This script creates a working deployment package for Azure App Service

Write-Host "Creating Azure deployment fix package..." -ForegroundColor Green

# Create a temporary directory for the deployment
$tempDir = "azure_fix_deployment"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy essential files
Write-Host "Copying essential files..." -ForegroundColor Yellow

# Copy the minimal app that we know works
Copy-Item "minimal_app.py" "$tempDir\app.py"

# Create a simple requirements.txt with only essential packages
@"
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
"@ | Out-File -FilePath "$tempDir\requirements.txt" -Encoding UTF8

# Create a startup command file for Azure
# Azure will look for this file and use it as the startup command
@"
python -m uvicorn app:app --host 0.0.0.0 --port 8000
"@ | Out-File -FilePath "$tempDir\startup.txt" -Encoding UTF8 -NoNewline

# Create a simple .env file
@"
ENVIRONMENT=production
APP_NAME=FoodXchange
"@ | Out-File -FilePath "$tempDir\.env" -Encoding UTF8

# Create runtime.txt to specify Python version
@"
python-3.12
"@ | Out-File -FilePath "$tempDir\runtime.txt" -Encoding UTF8 -NoNewline

# Create a health check endpoint in the app
$appContent = @"
from fastapi import FastAPI, Response
from datetime import datetime
import os
import sys

app = FastAPI(title="FoodXchange API")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": os.environ.get("ENVIRONMENT", "unknown")
    }

@app.head("/health")
async def health_head():
    return Response(status_code=200)

@app.get("/")
async def root():
    return {
        "message": "FoodXchange API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/health", "/docs", "/redoc"]
    }

@app.head("/")
async def root_head():
    return Response(status_code=200)

@app.get("/health/simple")
async def health_simple():
    return Response(content="OK", media_type="text/plain", status_code=200)

@app.head("/health/simple")
async def health_simple_head():
    return Response(status_code=200)

# Add error handler
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": str(request.url)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
"@

$appContent | Out-File -FilePath "$tempDir\app.py" -Encoding UTF8

# Create the deployment package
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path "$tempDir\*" -DestinationPath "azure_fix_deployment.zip" -Force

Write-Host "Deployment package created: azure_fix_deployment.zip" -ForegroundColor Green
Write-Host ""
Write-Host "To deploy this package:" -ForegroundColor Cyan
Write-Host "1. Go to Azure Portal" -ForegroundColor White
Write-Host "2. Navigate to your App Service (fdx-trading)" -ForegroundColor White
Write-Host "3. Go to Deployment Center" -ForegroundColor White
Write-Host "4. Use 'Local Git' or 'OneDeploy' to upload azure_fix_deployment.zip" -ForegroundColor White
Write-Host ""
Write-Host "Or use Azure CLI:" -ForegroundColor Cyan
Write-Host 'az webapp deploy --resource-group <your-rg> --name fdx-trading --src-path azure_fix_deployment.zip' -ForegroundColor White

# Clean up
Remove-Item $tempDir -Recurse -Force