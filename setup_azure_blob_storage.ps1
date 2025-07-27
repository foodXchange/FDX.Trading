# Azure Blob Storage Setup Script for FoodXchange
# This script sets up Azure Blob Storage service

Write-Host "=== Azure Blob Storage Setup for FoodXchange ===" -ForegroundColor Green

# Check if Azure CLI is installed
Write-Host "Checking Azure CLI installation..." -ForegroundColor Yellow
try {
    $azVersion = az --version
    Write-Host "Azure CLI is installed and working" -ForegroundColor Green
} catch {
    Write-Host "Azure CLI is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}

# Check if logged in to Azure
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "Logged in to Azure as: $($account.user.name)" -ForegroundColor Green
    Write-Host "Subscription: $($account.name)" -ForegroundColor Green
} catch {
    Write-Host "Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}

# Set variables
$resourceGroupName = "foodxchange-rg"
$storageAccountName = "foodxchangeblob2025"
$location = "westeurope"

# Check if resource group exists
Write-Host "Checking if resource group exists..." -ForegroundColor Yellow
$existingRG = az group show --name $resourceGroupName 2>$null
if ($existingRG) {
    Write-Host "Resource group '$resourceGroupName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating resource group '$resourceGroupName'..." -ForegroundColor Yellow
    az group create --name $resourceGroupName --location $location
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Resource group created successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to create resource group" -ForegroundColor Red
        exit 1
    }
}

# Check if storage account exists
Write-Host "Checking if storage account exists..." -ForegroundColor Yellow
$existingSA = az storage account show --name $storageAccountName --resource-group $resourceGroupName 2>$null
if ($existingSA) {
    Write-Host "Storage account '$storageAccountName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating storage account '$storageAccountName'..." -ForegroundColor Yellow
    az storage account create --name $storageAccountName --resource-group $resourceGroupName --location $location --sku Standard_LRS --kind StorageV2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Storage account created successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to create storage account" -ForegroundColor Red
        exit 1
    }
}

# Get storage account keys
Write-Host "Getting storage account keys..." -ForegroundColor Yellow
$keys = az storage account keys list --account-name $storageAccountName --resource-group $resourceGroupName | ConvertFrom-Json
if ($keys) {
    Write-Host "Storage account keys retrieved successfully" -ForegroundColor Green
    $key1 = $keys[0].value
    Write-Host "Key 1: $($key1.Substring(0, 10))..." -ForegroundColor Cyan
} else {
    Write-Host "Failed to get storage account keys" -ForegroundColor Red
    exit 1
}

# Create blob containers
Write-Host "Creating blob containers..." -ForegroundColor Yellow
$containers = @("uploads", "documents", "images", "exports")

foreach ($container in $containers) {
    Write-Host "Creating container: $container" -ForegroundColor Yellow
    az storage container create --name $container --account-name $storageAccountName --account-key $key1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Container '$container' created successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to create container '$container'" -ForegroundColor Red
    }
}

# Get connection string
Write-Host "Getting connection string..." -ForegroundColor Yellow
$connectionString = az storage account show-connection-string --name $storageAccountName --resource-group $resourceGroupName | ConvertFrom-Json
if ($connectionString) {
    Write-Host "Connection string retrieved successfully" -ForegroundColor Green
    Write-Host "Connection String: $($connectionString.connectionString.Substring(0, 50))..." -ForegroundColor Cyan
}

# Save configuration to file
Write-Host "Saving configuration..." -ForegroundColor Yellow
$config = @{
    StorageAccountName = $storageAccountName
    ResourceGroupName = $resourceGroupName
    Location = $location
    ConnectionString = $connectionString.connectionString
    Key1 = $key1
    Containers = $containers
}

$config | ConvertTo-Json | Out-File -FilePath "azure_blob_config.json" -Encoding UTF8
Write-Host "Configuration saved to azure_blob_config.json" -ForegroundColor Green

# Display summary
Write-Host "`n=== Setup Summary ===" -ForegroundColor Green
Write-Host "Storage Account: $storageAccountName" -ForegroundColor White
Write-Host "Resource Group: $resourceGroupName" -ForegroundColor White
Write-Host "Location: $location" -ForegroundColor White
Write-Host "Containers Created: $($containers -join ', ')" -ForegroundColor White
Write-Host "Configuration File: azure_blob_config.json" -ForegroundColor White

Write-Host "`nAzure Blob Storage setup completed successfully!" -ForegroundColor Green 