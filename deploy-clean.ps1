# Clean Azure Deployment Script for FoodXchange localhost:9000
param(
    [string]$ResourceGroupName = "foodxchange-clean",
    [string]$Location = "westeurope",
    [string]$AppName = "foodxchange-app"
)

$ACRName = "foodxchangeacr$(Get-Random -Maximum 9999)"

Write-Host "=== Clean Azure Deployment for FoodXchange localhost:9000 ===" -ForegroundColor Cyan

# Check Azure login
Write-Host "Checking Azure login..." -ForegroundColor Green
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Please login to Azure: az login" -ForegroundColor Red
    exit 1
}

# Create fresh resource group
Write-Host "Creating clean resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location
Write-Host "Resource group created: $ResourceGroupName" -ForegroundColor Green

# Create Container Registry
Write-Host "Creating Azure Container Registry..." -ForegroundColor Yellow
$acrResult = az acr create --resource-group $ResourceGroupName --name $ACRName --sku Basic --admin-enabled true --location $Location | ConvertFrom-Json
Write-Host "Container registry created: $ACRName" -ForegroundColor Green

# Get ACR credentials
Write-Host "Getting ACR credentials..." -ForegroundColor Yellow
$acrCredentials = az acr credential show --name $ACRName --resource-group $ResourceGroupName | ConvertFrom-Json
$loginServer = $acrResult.loginServer

# Create App Service Plan (Linux)
Write-Host "Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create --name "${AppName}-plan" --resource-group $ResourceGroupName --sku B1 --is-linux --location $Location
Write-Host "App Service Plan created" -ForegroundColor Green

# Create Web App for containers
Write-Host "Creating Web App..." -ForegroundColor Yellow
az webapp create --resource-group $ResourceGroupName --plan "${AppName}-plan" --name $AppName --deployment-container-image-name "mcr.microsoft.com/appsvc/staticsite:latest"
Write-Host "Web App created: $AppName" -ForegroundColor Green

# Configure Web App for port 9000
Write-Host "Configuring Web App for port 9000..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings WEBSITES_PORT=9000
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings WEBSITES_CONTAINER_START_TIME_LIMIT=600
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings ENVIRONMENT=production
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings DEBUG=False

# Get publish profile
Write-Host "Getting publish profile..." -ForegroundColor Yellow
$publishProfile = az webapp deployment list-publishing-profiles --resource-group $ResourceGroupName --name $AppName --xml

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "App Name: $AppName"
Write-Host "Container Registry: $ACRName"
Write-Host "Login Server: $loginServer"
Write-Host "Web App URL: https://$AppName.azurewebsites.net"

# Save GitHub secrets
$secretsContent = @"
AZURE_RESOURCE_GROUP=$ResourceGroupName
AZURE_REGISTRY_LOGIN_SERVER=$loginServer
AZURE_REGISTRY_USERNAME=$($acrCredentials.username)
AZURE_REGISTRY_PASSWORD=$($acrCredentials.passwords[0].value)

AZURE_WEBAPP_PUBLISH_PROFILE=$publishProfile
"@

$secretsContent | Out-File -FilePath "github-secrets-clean.txt" -Encoding UTF8

Write-Host "`nGitHub Secrets saved to: github-secrets-clean.txt" -ForegroundColor Green
Write-Host "Add these to: https://github.com/YOUR_REPO/settings/secrets/actions" -ForegroundColor Yellow