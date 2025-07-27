# Food Xchange Azure Monitor Setup Script
# This script sets up Azure Application Insights for monitoring your FastAPI application

Write-Host "🚀 Setting up Azure Monitor for Food Xchange" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "✅ Azure CLI found: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "✅ Logged in as: $($account.user.name)" -ForegroundColor Green
    Write-Host "   Subscription: $($account.name)" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}

# Get resource group (you can modify this)
$resourceGroup = Read-Host "Enter your Azure Resource Group name (or press Enter for 'foodxchange-rg')"
if ([string]::IsNullOrWhiteSpace($resourceGroup)) {
    $resourceGroup = "foodxchange-rg"
}

# Get location
$location = Read-Host "Enter your Azure region (or press Enter for 'eastus')"
if ([string]::IsNullOrWhiteSpace($location)) {
    $location = "eastus"
}

# Get app name
$appName = Read-Host "Enter your App Service name (or press Enter for 'foodxchange-app')"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = "foodxchange-app"
}

Write-Host "`n📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Resource Group: $resourceGroup" -ForegroundColor White
Write-Host "   Location: $location" -ForegroundColor White
Write-Host "   App Service: $appName" -ForegroundColor White
Write-Host "   App Insights: ${appName}-insights" -ForegroundColor White

$confirm = Read-Host "`nContinue with this configuration? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Setup cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🔧 Installing Application Insights extension..." -ForegroundColor Cyan
try {
    az extension add --name application-insights --yes
    Write-Host "✅ Application Insights extension installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Extension might already be installed, continuing..." -ForegroundColor Yellow
}

Write-Host "`n🏗️ Creating Application Insights resource..." -ForegroundColor Cyan
try {
    az monitor app-insights component create `
        --app "${appName}-insights" `
        --location $location `
        --resource-group $resourceGroup `
        --application-type web `
        --kind web
    
    Write-Host "✅ Application Insights created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Application Insights: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔑 Getting instrumentation key..." -ForegroundColor Cyan
try {
    $instrumentationKey = az monitor app-insights component show `
        --app "${appName}-insights" `
        --resource-group $resourceGroup `
        --query instrumentationKey -o tsv
    
    Write-Host "✅ Instrumentation Key: $instrumentationKey" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to get instrumentation key: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n📝 Creating configuration file..." -ForegroundColor Cyan
$configContent = @"
# Azure Application Insights Configuration
# Generated on $(Get-Date)

AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY=$instrumentationKey
AZURE_APP_INSIGHTS_CONNECTION_STRING=InstrumentationKey=$instrumentationKey;IngestionEndpoint=https://$location-0.in.applicationinsights.azure.com/
AZURE_APP_INSIGHTS_ENABLED=true

# Resource Information
AZURE_RESOURCE_GROUP=$resourceGroup
AZURE_LOCATION=$location
AZURE_APP_SERVICE=$appName
AZURE_APP_INSIGHTS_NAME=${appName}-insights
"@

$configContent | Out-File -FilePath "azure_monitor_config.env" -Encoding UTF8
Write-Host "✅ Configuration saved to azure_monitor_config.env" -ForegroundColor Green

Write-Host "`n🔗 Azure Portal Links:" -ForegroundColor Cyan
Write-Host "   Application Insights: https://portal.azure.com/#@$($account.tenantId)/resource/subscriptions/$($account.id)/resourceGroups/$resourceGroup/providers/Microsoft.Insights/components/${appName}-insights" -ForegroundColor Blue
Write-Host "   App Service: https://portal.azure.com/#@$($account.tenantId)/resource/subscriptions/$($account.id)/resourceGroups/$resourceGroup/providers/Microsoft.Web/sites/$appName" -ForegroundColor Blue

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Add the instrumentation key to your environment variables" -ForegroundColor White
Write-Host "2. Update your FastAPI app with Azure monitoring code" -ForegroundColor White
Write-Host "3. Deploy your updated application" -ForegroundColor White
Write-Host "4. Run the system monitor script to check status" -ForegroundColor White

Write-Host "`n✅ Azure Monitor setup completed successfully!" -ForegroundColor Green 