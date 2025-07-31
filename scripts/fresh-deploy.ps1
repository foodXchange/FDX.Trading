# Fresh Deployment Script for FoodXchange to Azure
# This script performs a complete fresh deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName = "foodxchange-prod-rg",
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "eastus",
    
    [string]$AppName = "foodxchange-app",
    [string]$Domain = "fdx.trading",
    [switch]$SkipCleanup = $false
)

# Variables
$ACR_NAME = "foodxchangeacr"
$PG_SERVER = "foodxchange-pg-server"
$REDIS_NAME = "foodxchange-redis"
$STORAGE_NAME = "foodxchangestorage"
$KEYVAULT_NAME = "foodxchange-kv"
$PLAN_NAME = "foodxchange-plan"

Write-Host "=== FoodXchange Fresh Deployment Script ===" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow
Write-Host "Domain: $Domain" -ForegroundColor Yellow
Write-Host ""

# Function to generate secure password
function New-SecurePassword {
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()"
    $password = ""
    for ($i = 0; $i -lt 32; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Green
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Azure CLI not found. Please install from: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Login to Azure
Write-Host "`nLogging in to Azure..." -ForegroundColor Green
az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    az login
}

# Phase 1: Cleanup (if not skipped)
if (-not $SkipCleanup) {
    Write-Host "`nPhase 1: Cleanup" -ForegroundColor Green
    $existingRg = az group exists --name $ResourceGroupName
    if ($existingRg -eq "true") {
        Write-Host "Deleting existing resource group..." -ForegroundColor Yellow
        az group delete --name $ResourceGroupName --yes --no-wait
        Write-Host "Waiting for deletion to complete (this may take several minutes)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        # Wait for deletion to complete
        while ((az group exists --name $ResourceGroupName) -eq "true") {
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 10
        }
        Write-Host " Done!" -ForegroundColor Green
    }
}

# Phase 2: Create Infrastructure
Write-Host "`nPhase 2: Creating Azure Infrastructure" -ForegroundColor Green

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create Container Registry
Write-Host "Creating Container Registry..." -ForegroundColor Yellow
az acr create `
    --name $ACR_NAME `
    --resource-group $ResourceGroupName `
    --sku Basic `
    --admin-enabled true

# Create PostgreSQL server
Write-Host "Creating PostgreSQL server..." -ForegroundColor Yellow
$pgPassword = New-SecurePassword
az postgres server create `
    --name $PG_SERVER `
    --resource-group $ResourceGroupName `
    --location $Location `
    --admin-user fdxadmin `
    --admin-password $pgPassword `
    --sku-name B_Gen5_1 `
    --version 11

# Create database
Write-Host "Creating database..." -ForegroundColor Yellow
az postgres db create `
    --name foodxchange `
    --resource-group $ResourceGroupName `
    --server-name $PG_SERVER

# Configure PostgreSQL firewall
Write-Host "Configuring PostgreSQL firewall..." -ForegroundColor Yellow
az postgres server firewall-rule create `
    --name AllowAllAzureIps `
    --resource-group $ResourceGroupName `
    --server-name $PG_SERVER `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0

# Create Redis Cache
Write-Host "Creating Redis Cache..." -ForegroundColor Yellow
az redis create `
    --name $REDIS_NAME `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku Basic `
    --vm-size c0

# Create Storage Account
Write-Host "Creating Storage Account..." -ForegroundColor Yellow
az storage account create `
    --name $STORAGE_NAME `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku Standard_LRS `
    --kind StorageV2

# Create storage container
$storageKey = az storage account keys list `
    --account-name $STORAGE_NAME `
    --query "[0].value" -o tsv

az storage container create `
    --name uploads `
    --account-name $STORAGE_NAME `
    --account-key $storageKey `
    --public-access blob

# Create Key Vault
Write-Host "Creating Key Vault..." -ForegroundColor Yellow
az keyvault create `
    --name $KEYVAULT_NAME `
    --resource-group $ResourceGroupName `
    --location $Location `
    --enable-rbac-authorization false

# Create App Service Plan
Write-Host "Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name $PLAN_NAME `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku B1 `
    --is-linux

# Create Web App
Write-Host "Creating Web App..." -ForegroundColor Yellow
az webapp create `
    --name $AppName `
    --resource-group $ResourceGroupName `
    --plan $PLAN_NAME `
    --deployment-container-image-name "mcr.microsoft.com/appsvc/staticsite:latest"

# Phase 3: Configure Secrets
Write-Host "`nPhase 3: Configuring Secrets" -ForegroundColor Green

# Get connection strings
$redisKey = az redis list-keys `
    --name $REDIS_NAME `
    --resource-group $ResourceGroupName `
    --query primaryKey -o tsv

$dbConnectionString = "postgresql://fdxadmin@${PG_SERVER}:${pgPassword}@${PG_SERVER}.postgres.database.azure.com:5432/foodxchange?sslmode=require"
$redisConnectionString = "rediss://:${redisKey}@${REDIS_NAME}.redis.cache.windows.net:6380/0"
$storageConnectionString = "DefaultEndpointsProtocol=https;AccountName=${STORAGE_NAME};AccountKey=${storageKey};EndpointSuffix=core.windows.net"

# Store secrets in Key Vault
Write-Host "Storing secrets in Key Vault..." -ForegroundColor Yellow
az keyvault secret set --vault-name $KEYVAULT_NAME --name "DatabaseUrl" --value $dbConnectionString | Out-Null
az keyvault secret set --vault-name $KEYVAULT_NAME --name "RedisUrl" --value $redisConnectionString | Out-Null
az keyvault secret set --vault-name $KEYVAULT_NAME --name "StorageConnectionString" --value $storageConnectionString | Out-Null
az keyvault secret set --vault-name $KEYVAULT_NAME --name "SecretKey" --value (New-SecurePassword) | Out-Null

# Phase 4: Build and Deploy
Write-Host "`nPhase 4: Building and Deploying Application" -ForegroundColor Green

# Get ACR credentials
$acrUsername = az acr credential show --name $ACR_NAME --query username -o tsv
$acrPassword = az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t foodxchange:latest -f Dockerfile.azure .

# Tag image
docker tag foodxchange:latest "${ACR_NAME}.azurecr.io/foodxchange:latest"

# Login to ACR
Write-Host "Logging in to Azure Container Registry..." -ForegroundColor Yellow
docker login "${ACR_NAME}.azurecr.io" -u $acrUsername -p $acrPassword

# Push image
Write-Host "Pushing Docker image..." -ForegroundColor Yellow
docker push "${ACR_NAME}.azurecr.io/foodxchange:latest"

# Configure Web App
Write-Host "Configuring Web App..." -ForegroundColor Yellow
az webapp config container set `
    --name $AppName `
    --resource-group $ResourceGroupName `
    --docker-custom-image-name "${ACR_NAME}.azurecr.io/foodxchange:latest" `
    --docker-registry-server-url "https://${ACR_NAME}.azurecr.io" `
    --docker-registry-server-user $acrUsername `
    --docker-registry-server-password $acrPassword

# Set app settings
Write-Host "Setting application configuration..." -ForegroundColor Yellow
az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroupName `
    --settings `
        ENVIRONMENT=production `
        DATABASE_URL=$dbConnectionString `
        REDIS_URL=$redisConnectionString `
        SECRET_KEY=(New-SecurePassword) `
        AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString `
        WEBSITES_PORT=8000 `
        WEBSITES_CONTAINER_START_TIME_LIMIT=600

# Phase 5: Configure Domain
Write-Host "`nPhase 5: Configuring Domain" -ForegroundColor Green

# Add custom domains
Write-Host "Adding custom domains..." -ForegroundColor Yellow
az webapp config hostname add `
    --webapp-name $AppName `
    --resource-group $ResourceGroupName `
    --hostname "www.$Domain"

az webapp config hostname add `
    --webapp-name $AppName `
    --resource-group $ResourceGroupName `
    --hostname $Domain

# Get app IP address
$appIp = az webapp show `
    --name $AppName `
    --resource-group $ResourceGroupName `
    --query outboundIpAddresses `
    --output tsv | ForEach-Object { $_.Split(',')[0] }

Write-Host "`nIMPORTANT: Update your domain DNS records:" -ForegroundColor Cyan
Write-Host "  A record for $Domain -> $appIp" -ForegroundColor Yellow
Write-Host "  A record for www.$Domain -> $appIp" -ForegroundColor Yellow
Write-Host "  OR" -ForegroundColor White
Write-Host "  CNAME record for www.$Domain -> ${AppName}.azurewebsites.net" -ForegroundColor Yellow

# Phase 6: Verification
Write-Host "`nPhase 6: Deployment Verification" -ForegroundColor Green

# Restart app
Write-Host "Restarting application..." -ForegroundColor Yellow
az webapp restart --name $AppName --resource-group $ResourceGroupName

Write-Host "Waiting for application to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check deployment
Write-Host "Checking deployment status..." -ForegroundColor Yellow
$appUrl = "https://${AppName}.azurewebsites.net"
try {
    $response = Invoke-WebRequest -Uri "$appUrl/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Health check failed. Check logs for details." -ForegroundColor Yellow
}

# Output summary
Write-Host "`n=== Deployment Summary ===" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor White
Write-Host "App URL: $appUrl" -ForegroundColor White
Write-Host "Domain: https://www.$Domain (pending DNS configuration)" -ForegroundColor White
Write-Host "Container Registry: ${ACR_NAME}.azurecr.io" -ForegroundColor White
Write-Host "PostgreSQL Server: ${PG_SERVER}.postgres.database.azure.com" -ForegroundColor White
Write-Host "Redis Cache: ${REDIS_NAME}.redis.cache.windows.net" -ForegroundColor White
Write-Host "Storage Account: ${STORAGE_NAME}.blob.core.windows.net" -ForegroundColor White
Write-Host "Key Vault: ${KEYVAULT_NAME}.vault.azure.net" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Green
Write-Host "1. Update DNS records for $Domain" -ForegroundColor White
Write-Host "2. Configure SSL certificate (run: az webapp config ssl create)" -ForegroundColor White
Write-Host "3. Set up GitHub secrets for CI/CD" -ForegroundColor White
Write-Host "4. Configure Azure OpenAI credentials in app settings" -ForegroundColor White
Write-Host "5. Monitor logs: az webapp log tail --name $AppName --resource-group $ResourceGroupName" -ForegroundColor White

# Save credentials
$credentialsFile = "deployment-credentials.txt"
@"
FoodXchange Deployment Credentials
==================================
Generated: $(Get-Date)

PostgreSQL:
  Server: ${PG_SERVER}.postgres.database.azure.com
  Database: foodxchange
  Username: fdxadmin
  Password: $pgPassword

Redis:
  Host: ${REDIS_NAME}.redis.cache.windows.net
  Port: 6380
  Password: $redisKey

Container Registry:
  Server: ${ACR_NAME}.azurecr.io
  Username: $acrUsername
  Password: $acrPassword

IMPORTANT: Store these credentials securely and delete this file!
"@ | Out-File -FilePath $credentialsFile

Write-Host "`nCredentials saved to: $credentialsFile" -ForegroundColor Yellow
Write-Host "⚠️  DELETE THIS FILE after storing credentials securely!" -ForegroundColor Red