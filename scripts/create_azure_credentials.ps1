# PowerShell script to create Azure service principal for GitHub Actions

# Variables
$appName = "foodxchange-github-actions"
$resourceGroup = "foodxchange-rg"
$subscriptionId = "493477d6-57ab-49c4-8229-a99c4425c65a"

Write-Host "Creating service principal for GitHub Actions..." -ForegroundColor Green

# Create service principal
$sp = az ad sp create-for-rbac `
    --name $appName `
    --role contributor `
    --scopes /subscriptions/$subscriptionId/resourceGroups/$resourceGroup `
    --json

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create service principal" -ForegroundColor Red
    exit 1
}

$spObject = $sp | ConvertFrom-Json

# Create the JSON credential for GitHub
$githubSecret = @{
    clientId = $spObject.appId
    clientSecret = $spObject.password
    subscriptionId = $subscriptionId
    tenantId = $spObject.tenant
} | ConvertTo-Json -Compress

Write-Host "`nAZURE_CREDENTIALS secret for GitHub:" -ForegroundColor Yellow
Write-Host $githubSecret -ForegroundColor Cyan

Write-Host "`nInstructions:" -ForegroundColor Green
Write-Host "1. Go to your GitHub repository settings"
Write-Host "2. Navigate to Secrets and variables > Actions"
Write-Host "3. Create a new secret named 'AZURE_CREDENTIALS'"
Write-Host "4. Paste the JSON above as the value"

Write-Host "`nService Principal Details:" -ForegroundColor Yellow
Write-Host "Client ID: $($spObject.appId)"
Write-Host "Tenant ID: $($spObject.tenant)"