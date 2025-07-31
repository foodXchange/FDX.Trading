# Setup Azure Infrastructure for FoodXchange Deployment
param(
    [string]$ResourceGroupName = "foodxchange-rg",
    [string]$Location = "eastus",
    [string]$AppName = "foodxchange-app",
    [string]$ACRName = "foodxchangeacr$(Get-Random -Maximum 9999)"
)

function Write-ColorOutput {
    param([string]$Color, [string]$Message)
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput Cyan "=== Setting up Azure Infrastructure for FoodXchange ==="
Write-Host ""

# Login check
Write-ColorOutput Green "Checking Azure login..."
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "✅ Logged in as: $($account.user.name)"
} catch {
    Write-ColorOutput Red "❌ Please login to Azure first: az login"
    exit 1
}

# Create resource group
Write-ColorOutput Green "Creating resource group..."
az group create --name $ResourceGroupName --location $Location
Write-Host "✅ Resource group created: $ResourceGroupName"

# Create container registry
Write-ColorOutput Green "Creating Azure Container Registry..."
az acr create --resource-group $ResourceGroupName --name $ACRName --sku Basic --admin-enabled true
Write-Host "✅ Container registry created: $ACRName"

# Get ACR credentials
$acrCredentials = az acr credential show --name $ACRName | ConvertFrom-Json
$loginServer = az acr show --name $ACRName --resource-group $ResourceGroupName --query loginServer --output tsv

# Create App Service Plan
Write-ColorOutput Green "Creating App Service Plan..."
az appservice plan create --name "${AppName}-plan" --resource-group $ResourceGroupName --sku B1 --is-linux
Write-Host "✅ App Service Plan created"

# Create Web App
Write-ColorOutput Green "Creating Web App..."
az webapp create --resource-group $ResourceGroupName --plan "${AppName}-plan" --name $AppName --deployment-container-image-name "mcr.microsoft.com/appsvc/staticsite:latest"
Write-Host "✅ Web App created: $AppName"

# Configure Web App for containers
Write-ColorOutput Green "Configuring Web App..."
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings WEBSITES_PORT=9000
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings WEBSITES_CONTAINER_START_TIME_LIMIT=600
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings ENVIRONMENT=production
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings DEBUG=False

# Get publish profile
Write-ColorOutput Green "Getting publish profile..."
$publishProfile = az webapp deployment list-publishing-profiles --resource-group $ResourceGroupName --name $AppName --xml

Write-ColorOutput Cyan "`n=== Azure Infrastructure Setup Complete ==="
Write-Host ""
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "App Name: $AppName"
Write-Host "Container Registry: $ACRName"
Write-Host "Login Server: $loginServer"
Write-Host "Web App URL: https://$AppName.azurewebsites.net"
Write-Host ""

Write-ColorOutput Yellow "📋 GitHub Secrets to Configure:"
Write-Host "AZURE_RESOURCE_GROUP = $ResourceGroupName"
Write-Host "AZURE_REGISTRY_LOGIN_SERVER = $loginServer"
Write-Host "AZURE_REGISTRY_USERNAME = $($acrCredentials.username)"
Write-Host "AZURE_REGISTRY_PASSWORD = $($acrCredentials.passwords[0].value)"
Write-Host ""
Write-Host "AZURE_WEBAPP_PUBLISH_PROFILE ="
Write-Host $publishProfile
Write-Host ""

Write-ColorOutput Green "🚀 Next Steps:"
Write-Host "1. Add the above secrets to your GitHub repository"
Write-Host "2. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
Write-Host "3. Commit and push your code to trigger deployment"
Write-Host "4. Monitor deployment at: https://github.com/YOUR_USERNAME/YOUR_REPO/actions"

# Save secrets to file for easy copying
$secretsFile = "github-secrets.txt"
@"
# GitHub Secrets for FoodXchange Deployment
AZURE_RESOURCE_GROUP=$ResourceGroupName
AZURE_REGISTRY_LOGIN_SERVER=$loginServer  
AZURE_REGISTRY_USERNAME=$($acrCredentials.username)
AZURE_REGISTRY_PASSWORD=$($acrCredentials.passwords[0].value)

AZURE_WEBAPP_PUBLISH_PROFILE=
$publishProfile
"@ | Out-File -FilePath $secretsFile

Write-ColorOutput Cyan "💾 Secrets saved to: $secretsFile"
Write-ColorOutput Red "⚠️  Keep this file secure and delete it after configuring GitHub!"