# FDX Azure Key Vault Setup Script
# This script securely stores the SQL password in Azure Key Vault

param(
    [string]$ResourceGroup = "rg-foodxchange",
    [string]$KeyVaultName = "kv-foodxchange",
    [string]$Location = "eastus"
)

Write-Host "Setting up Azure Key Vault for FDX..." -ForegroundColor Green

# Login to Azure
Write-Host "Logging in to Azure..." -ForegroundColor Yellow
az login

# Create Resource Group if it doesn't exist
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output none 2>$null

# Create Key Vault
Write-Host "Creating Key Vault..." -ForegroundColor Yellow
az keyvault create `
    --name $KeyVaultName `
    --resource-group $ResourceGroup `
    --location $Location `
    --enable-rbac-authorization false `
    --output none

# Store SQL Password in Key Vault (NEVER commit passwords to source control)
Write-Host "Storing SQL password in Key Vault..." -ForegroundColor Yellow
az keyvault secret set `
    --vault-name $KeyVaultName `
    --name "SqlPassword" `
    --value "FDX2030!" `
    --output none

# Store complete connection string with password (for migrations/admin tasks)
$sqlConnectionString = "Server=tcp:fdx-sql-prod.database.windows.net,1433;Database=fdxdb;User ID=fdxadmin;Password=FDX2030!;Encrypt=True;TrustServerCertificate=False;"

az keyvault secret set `
    --vault-name $KeyVaultName `
    --name "SqlConnectionFull" `
    --value $sqlConnectionString `
    --output none

Write-Host "Secrets stored successfully!" -ForegroundColor Green

# Get current user's object ID for Key Vault access
$currentUserObjectId = az ad signed-in-user show --query id --output tsv

Write-Host "Granting yourself full Key Vault access..." -ForegroundColor Yellow
az keyvault set-policy `
    --name $KeyVaultName `
    --object-id $currentUserObjectId `
    --secret-permissions all `
    --output none

Write-Host ""
Write-Host "Key Vault setup complete!" -ForegroundColor Green
Write-Host "Key Vault URI: https://$KeyVaultName.vault.azure.net/" -ForegroundColor Cyan
Write-Host ""
Write-Host "To grant App Service access:" -ForegroundColor Yellow
Write-Host "1. Enable Managed Identity on your App Service"
Write-Host "2. Run: az keyvault set-policy --name $KeyVaultName --object-id <app-identity-id> --secret-permissions get list"
Write-Host ""
Write-Host "Connection string for local development (with Azure CLI auth):" -ForegroundColor Yellow
Write-Host "Server=tcp:fdx-sql-prod.database.windows.net,1433;Database=fdxdb;Authentication=Active Directory Default;Encrypt=True;" -ForegroundColor Gray
Write-Host ""
Write-Host "WARNING: Delete this script after running to remove the password!" -ForegroundColor Red