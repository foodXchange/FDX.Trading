# PowerShell script to deploy Azure resources for FoodXchange

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName = "foodxchange-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$OpenAiLocation = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectName = "foodxchange"
)

Write-Host "Deploying Azure resources for FoodXchange..." -ForegroundColor Green

# Check if logged in to Azure
$context = Get-AzContext
if (-not $context) {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    Connect-AzAccount
}

# Create resource group if it doesn't exist
$rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
if (-not $rg) {
    Write-Host "Creating resource group: $ResourceGroupName in $Location" -ForegroundColor Yellow
    New-AzResourceGroup -Name $ResourceGroupName -Location $Location
} else {
    Write-Host "Using existing resource group: $ResourceGroupName" -ForegroundColor Green
}

# Deploy main resources
Write-Host "`nDeploying Azure resources..." -ForegroundColor Yellow
$deployment = New-AzResourceGroupDeployment `
    -ResourceGroupName $ResourceGroupName `
    -TemplateFile ".\azure\arm-templates\azure-resources.json" `
    -projectName $ProjectName `
    -location $Location `
    -openAiLocation $OpenAiLocation `
    -Verbose

if ($deployment.ProvisioningState -eq "Succeeded") {
    Write-Host "`nResources deployed successfully!" -ForegroundColor Green
    
    # Display outputs
    Write-Host "`nResource Information:" -ForegroundColor Cyan
    Write-Host "Storage Account: $($deployment.Outputs.storageAccountName.Value)"
    Write-Host "Document Intelligence Endpoint: $($deployment.Outputs.documentIntelligenceEndpoint.Value)"
    Write-Host "Translator Endpoint: $($deployment.Outputs.translatorEndpoint.Value)"
    Write-Host "OpenAI Endpoint: $($deployment.Outputs.openAiEndpoint.Value)"
    Write-Host "Computer Vision Endpoint: $($deployment.Outputs.computerVisionEndpoint.Value)"
    
    # Wait for OpenAI account to be fully provisioned
    Write-Host "`nWaiting for OpenAI account to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Deploy GPT-4 model
    Write-Host "`nDeploying GPT-4 model..." -ForegroundColor Yellow
    $openAiName = "$ProjectName-openai"
    
    $gptDeployment = New-AzResourceGroupDeployment `
        -ResourceGroupName $ResourceGroupName `
        -TemplateFile ".\azure\arm-templates\gpt4-deployment.json" `
        -openAiAccountName $openAiName `
        -Verbose
    
    if ($gptDeployment.ProvisioningState -eq "Succeeded") {
        Write-Host "`nGPT-4 deployment successful!" -ForegroundColor Green
        
        # Generate .env file
        Write-Host "`nGenerating .env file..." -ForegroundColor Yellow
        
        $envContent = @"
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=$($deployment.Outputs.storageConnectionString.Value)
AZURE_STORAGE_ACCOUNT_NAME=$($deployment.Outputs.storageAccountName.Value)
AZURE_STORAGE_ACCOUNT_KEY=$($deployment.Outputs.storageAccountKey.Value)

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=$($deployment.Outputs.documentIntelligenceEndpoint.Value)
AZURE_DOCUMENT_INTELLIGENCE_KEY=$($deployment.Outputs.documentIntelligenceKey.Value)

# Azure Translator
AZURE_TRANSLATOR_ENDPOINT=$($deployment.Outputs.translatorEndpoint.Value)
AZURE_TRANSLATOR_KEY=$($deployment.Outputs.translatorKey.Value)
AZURE_TRANSLATOR_REGION=$Location

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=$($deployment.Outputs.openAiEndpoint.Value)
AZURE_OPENAI_API_KEY=$($deployment.Outputs.openAiKey.Value)
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_VISION_DEPLOYMENT=gpt-4o

# Azure Computer Vision
AZURE_VISION_ENDPOINT=$($deployment.Outputs.computerVisionEndpoint.Value)
AZURE_VISION_KEY=$($deployment.Outputs.computerVisionKey.Value)

# Application Settings
DATABASE_URL=sqlite:///./foodxchange.db
SECRET_KEY=$(New-Guid).ToString()
ENVIRONMENT=development
"@
        
        $envContent | Out-File -FilePath ".env" -Encoding utf8
        Write-Host ".env file created successfully!" -ForegroundColor Green
        
        Write-Host "`nDeployment complete! Next steps:" -ForegroundColor Cyan
        Write-Host "1. Review the .env file and update any values as needed"
        Write-Host "2. Run 'python foodxchange/main.py' to start the application"
        Write-Host "3. The AI-powered import features are now ready to use!"
        
    } else {
        Write-Host "GPT-4 deployment failed. Please check the error messages." -ForegroundColor Red
    }
} else {
    Write-Host "Resource deployment failed. Please check the error messages." -ForegroundColor Red
}