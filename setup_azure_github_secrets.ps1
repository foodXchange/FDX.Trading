# Azure GitHub Secrets Setup Script
# This script helps create an Azure service principal and set up GitHub secrets for deployment

Write-Host "=== Azure GitHub Secrets Setup ===" -ForegroundColor Green
Write-Host "This script will help you set up Azure authentication for GitHub Actions" -ForegroundColor Yellow
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "✓ Azure CLI found (version: $($azVersion.'azure-cli'))" -ForegroundColor Green
} catch {
    Write-Host "✗ Azure CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "  https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "✓ Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "✗ Not logged in to Azure. Please run 'az login' first" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Step 1: Create Service Principal ===" -ForegroundColor Cyan

$subscriptionId = az account show --query id --output tsv
$resourceGroup = Read-Host "Enter your Azure resource group name (e.g., foodxchange-rg)"
$appName = Read-Host "Enter your Azure Web App name (e.g., foodxchange-app)"

Write-Host ""
Write-Host "Creating service principal..." -ForegroundColor Yellow

# Create service principal with contributor role on the resource group
$spResult = az ad sp create-for-rbac --name "github-actions-foodxchange" --role contributor --scopes "/subscriptions/$subscriptionId/resourceGroups/$resourceGroup" --output json | ConvertFrom-Json

Write-Host "✓ Service principal created successfully!" -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 2: Get Publish Profile ===" -ForegroundColor Cyan

# Get the publish profile
Write-Host "Getting publish profile for $appName..." -ForegroundColor Yellow
$publishProfile = az webapp deployment list-publishing-profiles --name $appName --resource-group $resourceGroup --output json | ConvertFrom-Json

Write-Host "✓ Publish profile retrieved!" -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 3: GitHub Secrets Setup ===" -ForegroundColor Cyan
Write-Host "You need to add these secrets to your GitHub repository:" -ForegroundColor Yellow
Write-Host ""

# Create the credentials JSON
$credentials = @{
    clientId = $spResult.appId
    clientSecret = $spResult.password
    subscriptionId = $subscriptionId
    tenantId = $spResult.tenant
}

$credentialsJson = $credentials | ConvertTo-Json -Compress

Write-Host "1. AZURE_CREDENTIALS (Repository Secret):" -ForegroundColor Magenta
Write-Host $credentialsJson -ForegroundColor White
Write-Host ""

Write-Host "2. AZUREAPPSERVICE_PUBLISHPROFILE (Repository Secret):" -ForegroundColor Magenta
Write-Host $publishProfile.publishUrl -ForegroundColor White
Write-Host ""

Write-Host "=== Instructions ===" -ForegroundColor Cyan
Write-Host "1. Go to your GitHub repository" -ForegroundColor Yellow
Write-Host "2. Click Settings > Secrets and variables > Actions" -ForegroundColor Yellow
Write-Host "3. Click 'New repository secret'" -ForegroundColor Yellow
Write-Host "4. Add AZURE_CREDENTIALS with the JSON above" -ForegroundColor Yellow
Write-Host "5. Add AZUREAPPSERVICE_PUBLISHPROFILE with the publish URL above" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== Security Note ===" -ForegroundColor Red
Write-Host "Keep these credentials secure and never commit them to your repository!" -ForegroundColor Yellow
Write-Host "The service principal has contributor access to your resource group." -ForegroundColor Yellow

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Add the secrets to GitHub" -ForegroundColor Yellow
Write-Host "2. Push your code to trigger the workflow" -ForegroundColor Yellow
Write-Host "3. Monitor the deployment in GitHub Actions" -ForegroundColor Yellow

# Save credentials to a file for reference (optional)
$saveToFile = Read-Host "Do you want to save these credentials to a file for reference? (y/n)"
if ($saveToFile -eq 'y' -or $saveToFile -eq 'Y') {
    $output = @{
        credentials = $credentials
        publishProfile = $publishProfile.publishUrl
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    $output | ConvertTo-Json -Depth 10 | Out-File -FilePath "azure_github_secrets.json" -Encoding UTF8
    Write-Host "✓ Credentials saved to azure_github_secrets.json" -ForegroundColor Green
    Write-Host "⚠️  Remember to delete this file after setting up GitHub secrets!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete! 🎉" -ForegroundColor Green 