# Azure Key Vault Setup Script
# Run this after creating your Azure resources

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup = "rg-foodxchange",
    
    [Parameter(Mandatory=$true)]
    [string]$KeyVaultName = "kv-foodxchange",
    
    [string]$Location = "eastus"
)

Write-Host "Setting up Azure Key Vault for FoodXchange..." -ForegroundColor Green

# Create Key Vault
Write-Host "Creating Key Vault..." -ForegroundColor Yellow
az keyvault create `
    --name $KeyVaultName `
    --resource-group $ResourceGroup `
    --location $Location `
    --enable-rbac-authorization false

# Get OpenAI key from existing resource
Write-Host "Retrieving Azure OpenAI key..." -ForegroundColor Yellow
$openAiKey = az cognitiveservices account keys list `
    --name "openai-foodxchange" `
    --resource-group $ResourceGroup `
    --query "key1" `
    --output tsv

# Store secrets in Key Vault
Write-Host "Storing secrets in Key Vault..." -ForegroundColor Yellow

# Azure OpenAI Key
az keyvault secret set `
    --vault-name $KeyVaultName `
    --name "AzureOpenAIKey" `
    --value $openAiKey

# Application Insights Connection String
$appInsightsConnection = az monitor app-insights component show `
    --app "appinsights-foodxchange" `
    --resource-group $ResourceGroup `
    --query "connectionString" `
    --output tsv

az keyvault secret set `
    --vault-name $KeyVaultName `
    --name "ApplicationInsightsConnection" `
    --value $appInsightsConnection

# SQL Connection String (for migrations/admin tasks only)
# Production apps should use Managed Identity
$sqlAdminPassword = Read-Host -Prompt "Enter SQL Admin Password" -AsSecureString
$sqlAdminPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sqlAdminPassword))

$sqlConnectionString = "Server=tcp:sql-foodxchange.database.windows.net,1433;Database=FoodXchange;User ID=sqladmin;Password=$sqlAdminPasswordPlain;Encrypt=True;TrustServerCertificate=False;"

az keyvault secret set `
    --vault-name $KeyVaultName `
    --name "SqlConnectionAdmin" `
    --value $sqlConnectionString

Write-Host "Granting App Service access to Key Vault..." -ForegroundColor Yellow

# Get Managed Identity principal IDs
$apiIdentity = az webapp identity show `
    --name "app-foodxchange-api" `
    --resource-group $ResourceGroup `
    --query "principalId" `
    --output tsv

$webIdentity = az webapp identity show `
    --name "app-foodxchange-web" `
    --resource-group $ResourceGroup `
    --query "principalId" `
    --output tsv

# Grant access to Key Vault
az keyvault set-policy `
    --name $KeyVaultName `
    --object-id $apiIdentity `
    --secret-permissions get list

az keyvault set-policy `
    --name $KeyVaultName `
    --object-id $webIdentity `
    --secret-permissions get list

Write-Host "Key Vault setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Key Vault URI: https://$KeyVaultName.vault.azure.net/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update App Service configuration to reference Key Vault"
Write-Host "2. Use @Microsoft.KeyVault() syntax in App Settings"
Write-Host ""