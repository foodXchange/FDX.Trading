# PowerShell script to create Azure services for FoodXchange

Write-Host "Creating Azure Services for FoodXchange..." -ForegroundColor Cyan

# Variables
$resourceGroup = "foodxchange-rg"
$location = "francecentral"
$storageAccount = "foodxchangestorage"
$openAIName = "foodxchange-openai"

# Check if logged in to Azure
Write-Host "`nChecking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if (!$account) {
    Write-Host "Not logged in. Running 'az login'..." -ForegroundColor Yellow
    az login
}

# 1. Create Storage Account
Write-Host "`n1. Creating Storage Account..." -ForegroundColor Green
az storage account create `
    --name $storageAccount `
    --resource-group $resourceGroup `
    --location $location `
    --sku Standard_LRS `
    --kind StorageV2 `
    --access-tier Hot

# Get Storage Connection String
Write-Host "`nGetting Storage Connection String..." -ForegroundColor Yellow
$storageConnString = az storage account show-connection-string `
    --name $storageAccount `
    --resource-group $resourceGroup `
    --query connectionString `
    --output tsv

Write-Host "Storage Connection String:" -ForegroundColor Green
Write-Host $storageConnString -ForegroundColor Cyan
Write-Host "`nAdd this to your .env file:" -ForegroundColor Yellow
Write-Host "AZURE_STORAGE_CONNECTION_STRING=$storageConnString" -ForegroundColor White

# 2. Create OpenAI Service
Write-Host "`n2. Creating Azure OpenAI Service..." -ForegroundColor Green
az cognitiveservices account create `
    --name $openAIName `
    --resource-group $resourceGroup `
    --location $location `
    --kind OpenAI `
    --sku S0 `
    --yes

# Get OpenAI Endpoint
Write-Host "`nGetting OpenAI Endpoint..." -ForegroundColor Yellow
$openAIEndpoint = az cognitiveservices account show `
    --name $openAIName `
    --resource-group $resourceGroup `
    --query properties.endpoint `
    --output tsv

# Get OpenAI Key
Write-Host "Getting OpenAI Key..." -ForegroundColor Yellow
$openAIKey = az cognitiveservices account keys list `
    --name $openAIName `
    --resource-group $resourceGroup `
    --query key1 `
    --output tsv

Write-Host "`nOpenAI Configuration:" -ForegroundColor Green
Write-Host "Endpoint: $openAIEndpoint" -ForegroundColor Cyan
Write-Host "Key: $openAIKey" -ForegroundColor Cyan

Write-Host "`nAdd these to your .env file:" -ForegroundColor Yellow
Write-Host "AZURE_OPENAI_API_KEY=$openAIKey" -ForegroundColor White
Write-Host "AZURE_OPENAI_ENDPOINT=$openAIEndpoint" -ForegroundColor White
Write-Host "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4" -ForegroundColor White

Write-Host "`n3. Next Steps:" -ForegroundColor Green
Write-Host "- Go to Azure Portal > OpenAI > Model deployments" -ForegroundColor White
Write-Host "- Deploy a 'gpt-4' or 'gpt-35-turbo' model" -ForegroundColor White
Write-Host "- Update your .env file with the credentials above" -ForegroundColor White

Write-Host "`nDone! Services created successfully." -ForegroundColor Green