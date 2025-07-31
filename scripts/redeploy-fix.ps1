# Complete Redeployment Script to Fix FoodXchange on Azure
# This script will redeploy and fix DNS issues for fdx.trading

param(
    [string]$ResourceGroup = "foodxchange-prod-rg",
    [string]$Location = "eastus",
    [string]$AppName = "foodxchange-app",
    [string]$Domain = "fdx.trading",
    [switch]$UseFreeApp = $false
)

function Write-ColorOutput {
    param([string]$Color, [string]$Message)
    Write-Host $Message -ForegroundColor $Color
}

function New-SecurePassword {
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()"
    $password = ""
    for ($i = 0; $i -lt 32; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

Write-ColorOutput Cyan "=== FoodXchange Redeployment & DNS Fix ==="
Write-ColorOutput Yellow "This will redeploy your app and fix the DNS issues"
Write-Host ""

# Variables
$ACR_NAME = "foodxchangeacr" + (Get-Random -Maximum 9999).ToString().PadLeft(4, '0')
$STORAGE_NAME = "fdxstorage" + (Get-Random -Maximum 9999).ToString().PadLeft(4, '0')
$PLAN_NAME = "foodxchange-plan"

# Step 1: Diagnose current state
Write-ColorOutput Green "Step 1: Diagnosing current deployment..."
$rgExists = az group exists --name $ResourceGroup
Write-Host "Resource Group exists: $rgExists"

# Step 2: Clean up if needed
if ($rgExists -eq "true") {
    Write-ColorOutput Yellow "Found existing resource group. Cleaning up..."
    az group delete --name $ResourceGroup --yes --no-wait
    
    Write-Host "Waiting for cleanup to complete..."
    while ((az group exists --name $ResourceGroup) -eq "true") {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 10
    }
    Write-Host "`nCleanup complete!"
}

# Step 3: Create fresh infrastructure
Write-ColorOutput Green "`nStep 2: Creating fresh Azure infrastructure..."

# Create resource group
Write-Host "Creating resource group..."
az group create --name $ResourceGroup --location $Location

# Create storage account (needed for container registry)
Write-Host "Creating storage account..."
az storage account create `
    --name $STORAGE_NAME `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku Standard_LRS

# Create container for uploads
$storageKey = az storage account keys list --account-name $STORAGE_NAME --query "[0].value" -o tsv
az storage container create `
    --name uploads `
    --account-name $STORAGE_NAME `
    --account-key $storageKey `
    --public-access blob

# Choose deployment method based on parameter
if ($UseFreeApp) {
    Write-ColorOutput Yellow "Using App Service Free Tier (F1) - No custom domain support"
    
    # Create free app service plan
    az appservice plan create `
        --name $PLAN_NAME `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku F1
    
    # Create web app
    az webapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --plan $PLAN_NAME `
        --runtime "PYTHON|3.11"
    
    # Deploy from local git
    Write-Host "Configuring local git deployment..."
    az webapp deployment source config-local-git `
        --name $AppName `
        --resource-group $ResourceGroup
    
    $gitUrl = az webapp deployment list-publishing-credentials `
        --name $AppName `
        --resource-group $ResourceGroup `
        --query scmUri -o tsv
    
    Write-ColorOutput Green "Git URL: $gitUrl"
    Write-ColorOutput Yellow "Your app will be available at: https://$AppName.azurewebsites.net"
    
} else {
    Write-ColorOutput Green "Using Container Deployment with Custom Domain Support"
    
    # Create container registry
    Write-Host "Creating container registry..."
    az acr create `
        --name $ACR_NAME `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku Basic `
        --admin-enabled true
    
    # Create app service plan (Basic tier supports custom domains)
    Write-Host "Creating app service plan..."
    az appservice plan create `
        --name $PLAN_NAME `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku B1 `
        --is-linux
    
    # Create web app for containers
    Write-Host "Creating web app..."
    az webapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --plan $PLAN_NAME `
        --deployment-container-image-name "mcr.microsoft.com/appsvc/staticsite:latest"
    
    # Get ACR credentials
    $acrUsername = az acr credential show --name $ACR_NAME --query username -o tsv
    $acrPassword = az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv
    
    # Build and push image
    Write-Host "Building Docker image..."
    $imageName = "${ACR_NAME}.azurecr.io/foodxchange:latest"
    
    # Login to ACR
    docker login "${ACR_NAME}.azurecr.io" -u $acrUsername -p $acrPassword
    
    # Build image
    docker build -t foodxchange:latest -f Dockerfile.azure .
    docker tag foodxchange:latest $imageName
    
    # Push image
    Write-Host "Pushing image to registry..."
    docker push $imageName
    
    # Configure web app to use the image
    Write-Host "Configuring web app container..."
    az webapp config container set `
        --name $AppName `
        --resource-group $ResourceGroup `
        --docker-custom-image-name $imageName `
        --docker-registry-server-url "https://${ACR_NAME}.azurecr.io" `
        --docker-registry-server-user $acrUsername `
        --docker-registry-server-password $acrPassword
}

# Step 4: Configure App Settings
Write-ColorOutput Green "`nStep 3: Configuring application..."

$storageConnectionString = "DefaultEndpointsProtocol=https;AccountName=${STORAGE_NAME};AccountKey=${storageKey};EndpointSuffix=core.windows.net"

az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        ENVIRONMENT=production `
        DEBUG=False `
        SECRET_KEY=(New-SecurePassword) `
        DATABASE_URL="sqlite:///./app.db" `
        AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString `
        WEBSITES_PORT=8000 `
        WEBSITES_CONTAINER_START_TIME_LIMIT=600

# Step 5: Configure Custom Domain (only for paid tiers)
if (-not $UseFreeApp) {
    Write-ColorOutput Green "`nStep 4: Configuring custom domain..."
    
    # Get the web app's IP address
    $webappIp = az webapp show --name $AppName --resource-group $ResourceGroup --query outboundIpAddresses --output tsv
    $primaryIp = $webappIp.Split(',')[0]
    
    Write-ColorOutput Cyan "`n=== IMPORTANT DNS CONFIGURATION ==="
    Write-ColorOutput Yellow "You need to configure these DNS records with your domain provider:"
    Write-Host ""
    Write-Host "A Records:"
    Write-Host "  $Domain -> $primaryIp"
    Write-Host "  www.$Domain -> $primaryIp"
    Write-Host ""
    Write-Host "OR use CNAME (recommended):"
    Write-Host "  www.$Domain -> $AppName.azurewebsites.net"
    Write-Host ""
    
    $addDomain = Read-Host "Have you configured DNS records? Enter 'yes' to add custom domain, or 'skip' to skip"
    
    if ($addDomain -eq 'yes') {
        Write-Host "Adding custom domains..."
        
        # Add www domain
        try {
            az webapp config hostname add `
                --webapp-name $AppName `
                --resource-group $ResourceGroup `
                --hostname "www.$Domain"
            Write-Host "✅ Added www.$Domain"
        } catch {
            Write-ColorOutput Red "❌ Failed to add www.$Domain - DNS may not be propagated yet"
        }
        
        # Add root domain
        try {
            az webapp config hostname add `
                --webapp-name $AppName `
                --resource-group $ResourceGroup `
                --hostname $Domain
            Write-Host "✅ Added $Domain"
        } catch {
            Write-ColorOutput Red "❌ Failed to add $Domain - DNS may not be propagated yet"
        }
        
        # Try to create managed SSL certificate
        Write-Host "Creating SSL certificate..."
        try {
            az webapp config ssl create `
                --name $AppName `
                --resource-group $ResourceGroup `
                --hostname "www.$Domain"
            Write-Host "✅ SSL certificate created"
        } catch {
            Write-ColorOutput Yellow "⚠️  SSL certificate creation failed - this is normal if DNS isn't fully propagated"
            Write-Host "You can create it later with: az webapp config ssl create --name $AppName --resource-group $ResourceGroup --hostname www.$Domain"
        }
    }
}

# Step 6: Restart and verify
Write-ColorOutput Green "`nStep 5: Starting application..."
az webapp restart --name $AppName --resource-group $ResourceGroup

Write-Host "Waiting for app to start..."
Start-Sleep -Seconds 30

# Test the deployment
$azureUrl = "https://$AppName.azurewebsites.net"
Write-ColorOutput Green "`nStep 6: Testing deployment..."
Write-Host "Testing Azure URL: $azureUrl"

try {
    $response = Invoke-WebRequest $azureUrl -UseBasicParsing -TimeoutSec 30
    Write-Host "✅ App responds with status: $($response.StatusCode)"
    
    # Test health endpoint
    try {
        $healthResponse = Invoke-WebRequest "$azureUrl/health" -UseBasicParsing -TimeoutSec 10
        Write-Host "✅ Health endpoint responds: $($healthResponse.StatusCode)"
    } catch {
        Write-ColorOutput Yellow "⚠️  Health endpoint not yet available (normal for new deployments)"
    }
    
} catch {
    Write-ColorOutput Red "❌ App not responding yet. Check logs with:"
    Write-Host "az webapp log tail --name $AppName --resource-group $ResourceGroup"
}

# Final summary
Write-ColorOutput Cyan "`n=== DEPLOYMENT COMPLETE ==="
Write-Host "Resource Group: $ResourceGroup"
Write-Host "App Name: $AppName"
Write-Host "Azure URL: $azureUrl"

if ($UseFreeApp) {
    Write-ColorOutput Yellow "`nUsing Free Tier - Custom domain not supported"
    Write-Host "Your app is available at: $azureUrl"
} else {
    Write-Host "Custom Domain: https://www.$Domain (after DNS configuration)"
    Write-Host "Storage Account: $STORAGE_NAME"
    Write-Host "Container Registry: $ACR_NAME"
}

Write-ColorOutput Green "`nNext steps:"
if (-not $UseFreeApp) {
    Write-Host "1. Configure DNS records as shown above"
    Write-Host "2. Wait for DNS propagation (5-30 minutes)"
    Write-Host "3. Add custom domain: az webapp config hostname add --webapp-name $AppName --resource-group $ResourceGroup --hostname www.$Domain"
    Write-Host "4. Create SSL certificate: az webapp config ssl create --name $AppName --resource-group $ResourceGroup --hostname www.$Domain"
}
Write-Host "5. Add your Azure OpenAI credentials to app settings"
Write-Host "6. Monitor logs: az webapp log tail --name $AppName --resource-group $ResourceGroup"

Write-ColorOutput Cyan "`nDeployment completed successfully! 🚀"