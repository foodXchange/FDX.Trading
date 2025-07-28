# Create Azure Service Principal for GitHub Actions
Write-Host "Creating Azure Service Principal for GitHub Actions..." -ForegroundColor Green

# Variables
$appName = "github-actions-foodxchange"
$resourceGroup = "foodxchange-rg"

# Get subscription ID
Write-Host "Getting subscription information..." -ForegroundColor Yellow
$subscriptionId = az account show --query id -o tsv

if (!$subscriptionId) {
    Write-Host "Error: Not logged into Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

Write-Host "Subscription ID: $subscriptionId" -ForegroundColor Cyan

# Create service principal
Write-Host "`nCreating service principal..." -ForegroundColor Yellow
$spOutput = az ad sp create-for-rbac `
    --name $appName `
    --role contributor `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroup `
    --sdk-auth

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create service principal" -ForegroundColor Red
    exit 1
}

# Save to file
$spOutput | Set-Content -Path "azure_credentials.json"

Write-Host "`nService Principal created successfully!" -ForegroundColor Green
Write-Host "`nIMPORTANT: Add this JSON as a GitHub secret named 'AZURE_CREDENTIALS'" -ForegroundColor Yellow
Write-Host "The credentials have been saved to: azure_credentials.json" -ForegroundColor Cyan
Write-Host "`nSteps to add to GitHub:" -ForegroundColor Yellow
Write-Host "1. Copy the content of azure_credentials.json" -ForegroundColor White
Write-Host "2. Go to: https://github.com/YOUR_USERNAME/FoodXchange/settings/secrets/actions/new" -ForegroundColor White
Write-Host "3. Name: AZURE_CREDENTIALS" -ForegroundColor White
Write-Host "4. Value: Paste the JSON content" -ForegroundColor White
Write-Host "5. Click 'Add secret'" -ForegroundColor White

# Also create a more detailed instructions file
@"
GITHUB SECRETS CONFIGURATION
============================

1. AZURE_CREDENTIALS (Required)
   - Copy the entire content from azure_credentials.json
   - This allows GitHub Actions to deploy to Azure

2. AZURE_WEBAPP_PUBLISH_PROFILE (Alternative to AZURE_CREDENTIALS)
   - Download from Azure Portal > App Service > Get publish profile
   - Use this if you prefer not to create a service principal

3. Additional Secrets (Optional but recommended):
   - AZURE_OPENAI_API_KEY: f9061473a6754ec1b572f674d8b28b07
   - AZURE_OPENAI_ENDPOINT: https://swedencentral.api.cognitive.microsoft.com/
   - DATABASE_URL: (your database connection string)

Choose either method 1 (AZURE_CREDENTIALS) or method 2 (AZURE_WEBAPP_PUBLISH_PROFILE)
Both work, but AZURE_CREDENTIALS is more flexible for complex deployments.
"@ | Set-Content GITHUB_SECRETS_INSTRUCTIONS.txt

Write-Host "`nInstructions saved to: GITHUB_SECRETS_INSTRUCTIONS.txt" -ForegroundColor Green

# Don't forget to add azure_credentials.json to .gitignore
if (!(Select-String -Path .gitignore -Pattern "azure_credentials.json" -Quiet)) {
    Add-Content -Path .gitignore -Value "`nazure_credentials.json"
    Write-Host "`nAdded azure_credentials.json to .gitignore for security" -ForegroundColor Yellow
}