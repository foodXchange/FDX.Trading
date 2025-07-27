# Quick Deploy Guide for FoodXchange

## Prerequisites
- Azure CLI installed ✅
- Azure account

## Step 1: Login to Azure
Open PowerShell or Command Prompt and run:
```bash
az login
```
This will open a browser. Complete the login process.

## Step 2: Deploy Using Scripts

### Option A: Use PowerShell Script
```powershell
.\deploy_and_configure.ps1
```

### Option B: Use Python Script
```bash
python deploy_azure_fixed.py
```

### Option C: Manual Commands
Run these commands one by one:

```bash
# Set variables
$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"
$planName = "foodxchange-plan"
$location = "East US"

# Create resource group
az group create --name $resourceGroup --location "$location"

# Create App Service Plan
az appservice plan create --name $planName --resource-group $resourceGroup --sku B1 --is-linux

# Create Web App
az webapp create --resource-group $resourceGroup --plan $planName --name $appName --runtime "PYTHON:3.12"

# Configure startup command
az webapp config set --resource-group $resourceGroup --name $appName --startup-file "gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app"

# Create deployment package
python create_deployment_package.py

# Deploy the app
az webapp deployment source config-zip --resource-group $resourceGroup --name $appName --src foodxchange_deployment.zip
```

## Step 3: Configure Azure OpenAI
After deployment, configure your Azure OpenAI settings:

```bash
az webapp config appsettings set --resource-group foodxchange-rg --name foodxchange-app --settings AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" AZURE_OPENAI_API_KEY="your-api-key" AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o" AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```

## Step 4: Get Publish Profile for GitHub Actions
```bash
az webapp deployment list-publishing-profiles --name foodxchange-app --resource-group foodxchange-rg --xml > publish_profile.xml
```

Then:
1. Copy the contents of `publish_profile.xml`
2. Go to GitHub repository → Settings → Secrets and variables → Actions
3. Add new secret: `AZUREAPPSERVICE_PUBLISHPROFILE`
4. Paste the XML content

## Verification
Your app will be available at:
- Main URL: https://foodxchange-app.azurewebsites.net
- Health Check: https://foodxchange-app.azurewebsites.net/health
- System Status: https://foodxchange-app.azurewebsites.net/system-status

## Troubleshooting
If deployment fails:
1. Check Azure subscription quota
2. Ensure unique app name
3. Check logs: `az webapp log tail --name foodxchange-app --resource-group foodxchange-rg`