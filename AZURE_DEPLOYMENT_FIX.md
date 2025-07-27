# Azure Deployment Fix Guide

## Issue
The GitHub Actions deployment is failing because Azure credentials are not configured. The workflow expects Service Principal credentials as GitHub secrets.

## Solution Options

### Option 1: Deploy Locally (Recommended for Quick Deployment)
Use the local deployment script that's already configured:

```bash
# Run this from PowerShell
.\deploy_fixed.bat
```

Or directly:
```bash
python deploy_azure_fixed.py
```

### Option 2: Fix GitHub Actions Deployment

1. **Create Azure Service Principal**
   ```bash
   # Login to Azure
   az login
   
   # Create service principal
   az ad sp create-for-rbac --name "foodxchange-github-sp" --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/foodxchange-rg --sdk-auth
   ```

2. **Add GitHub Secrets**
   Go to your GitHub repository → Settings → Secrets and variables → Actions
   
   Add these secrets from the service principal output:
   - `AZUREAPPSERVICE_CLIENTID_4B1775FDD2034EFA9CE58403665C630D`
   - `AZUREAPPSERVICE_TENANTID_9960A9C9DAB845D18B7E9C272DA67C6A`
   - `AZUREAPPSERVICE_SUBSCRIPTIONID_493477D657AB49C48229A99C4425C65A`

### Option 3: Use Publish Profile (Simpler)
Modify the workflow to use publish profile instead:

1. Get publish profile:
   ```bash
   az webapp deployment list-publishing-profiles --name foodxchange-app --resource-group foodxchange-rg --xml
   ```

2. Add as GitHub secret: `AZUREAPPSERVICE_PUBLISHPROFILE`

3. Update workflow to use publish profile.

## Quick Deployment Steps

1. Ensure you're logged into Azure CLI:
   ```bash
   az login
   ```

2. Run the deployment:
   ```bash
   .\deploy_fixed.bat
   ```

3. The script will:
   - Create resource group
   - Create App Service Plan
   - Create Web App
   - Deploy your application
   - Configure OpenAI settings

## Verify Deployment
After deployment, check:
- Health endpoint: https://foodxchange-app.azurewebsites.net/health
- System status: https://foodxchange-app.azurewebsites.net/system-status