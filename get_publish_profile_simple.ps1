# Simple Publish Profile Setup for GitHub Actions
Write-Host "=== Simple Azure Publish Profile Setup ===" -ForegroundColor Green

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "Azure CLI found (version: $($azVersion.'azure-cli'))" -ForegroundColor Green
} catch {
    Write-Host "Azure CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Not logged in to Azure. Please run 'az login' first" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Get Publish Profile ===" -ForegroundColor Cyan

$resourceGroup = Read-Host "Enter your Azure resource group name (e.g., foodxchange-rg)"
$appName = Read-Host "Enter your Azure Web App name (e.g., foodxchange-app)"

Write-Host ""
Write-Host "Getting publish profile for $appName..." -ForegroundColor Yellow

# Get the publish profile
$publishProfile = az webapp deployment list-publishing-profiles --name $appName --resource-group $resourceGroup --output json | ConvertFrom-Json

Write-Host "Publish profile retrieved!" -ForegroundColor Green

Write-Host ""
Write-Host "=== GitHub Secret Setup ===" -ForegroundColor Cyan
Write-Host "You need to add this secret to your GitHub repository:" -ForegroundColor Yellow
Write-Host ""

Write-Host "AZUREAPPSERVICE_PUBLISHPROFILE (Repository Secret):" -ForegroundColor Magenta
Write-Host $publishProfile.publishUrl -ForegroundColor White
Write-Host ""

Write-Host "=== Instructions ===" -ForegroundColor Cyan
Write-Host "1. Go to your GitHub repository" -ForegroundColor Yellow
Write-Host "2. Click Settings - Secrets and variables - Actions" -ForegroundColor Yellow
Write-Host "3. Click 'New repository secret'" -ForegroundColor Yellow
Write-Host "4. Name: AZUREAPPSERVICE_PUBLISHPROFILE" -ForegroundColor Yellow
Write-Host "5. Value: Copy the publish URL above" -ForegroundColor Yellow
Write-Host "6. Click 'Add secret'" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Add the secret to GitHub" -ForegroundColor Yellow
Write-Host "2. Push your code to trigger the workflow" -ForegroundColor Yellow
Write-Host "3. Monitor the deployment in GitHub Actions" -ForegroundColor Yellow

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green 