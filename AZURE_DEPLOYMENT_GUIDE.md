# FoodXchange Azure Deployment Guide

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

#### Windows Users
```bash
# Double-click or run in Command Prompt
deploy.bat
```

#### PowerShell Users
```powershell
# Run in PowerShell
.\azure-deploy.ps1
```

#### Manual Python Script
```bash
python azure_deploy.py
```

### Option 2: Manual Deployment

Follow the step-by-step instructions below.

## 📋 Prerequisites

### 1. Azure Account
- [Create an Azure account](https://azure.microsoft.com/free/) (free tier available)
- Get your subscription ID

### 2. Azure CLI
```bash
# Windows (using winget)
winget install Microsoft.AzureCLI

# Windows (using Chocolatey)
choco install azure-cli

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 3. Python 3.8+
```bash
# Verify Python installation
python --version
```

### 4. Login to Azure
```bash
az login
```

## 🔧 Step-by-Step Deployment

### 1. Prepare Your Application

Your FoodXchange application is already configured for Azure deployment with:
- ✅ FastAPI application (`foodxchange/main.py`)
- ✅ Azure-optimized `web.config`
- ✅ Startup script (`startup.py`)
- ✅ Requirements file (`requirements.txt`)
- ✅ Deployment scripts

### 2. Choose Your Deployment Method

#### Method A: Automated Script (Recommended)
```bash
# Run the automated deployment script
python azure_deploy.py
```

The script will:
- ✅ Check prerequisites
- ✅ Create Azure resources (if needed)
- ✅ Package your application
- ✅ Deploy to Azure App Service
- ✅ Verify deployment
- ✅ Clean up temporary files

#### Method B: Manual Azure CLI
```bash
# 1. Create resource group
az group create --name foodxchange-rg --location "East US"

# 2. Create app service plan
az appservice plan create --name foodxchange-plan --resource-group foodxchange-rg --sku B1 --is-linux

# 3. Create web app
az webapp create --name foodxchange-app --resource-group foodxchange-rg --plan foodxchange-plan --runtime "PYTHON|3.12"

# 4. Configure app settings
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true \
  PYTHON_VERSION=3.12 \
  WEBSITES_PORT=8000 \
  ENVIRONMENT=production \
  DEBUG=False

# 5. Deploy from local directory
az webapp deployment source config-local-git --name foodxchange-app --resource-group foodxchange-rg
```

### 3. Configure Environment Variables

After deployment, configure your environment variables in Azure:

```bash
# Set database connection
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  DATABASE_URL="your-database-connection-string"

# Set secret key
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  SECRET_KEY="your-secret-key"

# Set Azure OpenAI settings (if using)
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  AZURE_OPENAI_API_KEY="your-openai-key" \
  AZURE_OPENAI_ENDPOINT="your-openai-endpoint"
```

### 4. Verify Deployment

```bash
# Check app status
az webapp show --name foodxchange-app --resource-group foodxchange-rg

# Check logs
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg

# Test health endpoint
curl https://foodxchange-app.azurewebsites.net/health
```

## 🌐 Access Your Application

Your application will be available at:
- **URL**: `https://your-app-name.azurewebsites.net`
- **Health Check**: `https://your-app-name.azurewebsites.net/health`
- **API Docs**: `https://your-app-name.azurewebsites.net/docs`

## 🔧 Post-Deployment Configuration

### 1. Database Setup

#### Option A: Azure Database for PostgreSQL
```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group foodxchange-rg \
  --name foodxchange-db \
  --admin-user adminuser \
  --admin-password YourPassword123! \
  --sku-name Standard_B1ms \
  --version 13

# Create database
az postgres flexible-server db create \
  --resource-group foodxchange-rg \
  --server-name foodxchange-db \
  --database-name foodxchange
```

#### Option B: Use Existing Database
Update the `DATABASE_URL` in Azure App Settings with your existing database connection string.

### 2. Custom Domain Setup

```bash
# Add custom domain
az webapp config hostname add --webapp-name foodxchange-app --resource-group foodxchange-rg --hostname www.yourdomain.com

# Configure SSL certificate
az webapp config ssl bind --certificate-thumbprint <thumbprint> --ssl-type SNI --name foodxchange-app --resource-group foodxchange-rg
```

### 3. Monitoring and Logging

#### Application Insights
```bash
# Create Application Insights
az monitor app-insights component create --app foodxchange-insights --location "East US" --resource-group foodxchange-rg --application-type web

# Get instrumentation key
az monitor app-insights component show --app foodxchange-insights --resource-group foodxchange-rg --query instrumentationKey
```

#### Log Analytics
```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create --resource-group foodxchange-rg --workspace-name foodxchange-logs
```

## 🔄 Continuous Deployment

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'foodxchange-app'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: .
```

### Azure DevOps

Set up Azure DevOps pipeline for automated deployments.

## 🛠️ Troubleshooting

### Common Issues

#### 1. App Won't Start
```bash
# Check logs
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg

# Check app settings
az webapp config appsettings list --name foodxchange-app --resource-group foodxchange-rg
```

#### 2. Import Errors
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility
- Verify file paths in `startup.py`

#### 3. Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check firewall rules for database access
- Ensure database server is running

#### 4. Performance Issues
- Scale up App Service plan if needed
- Enable Application Insights for monitoring
- Optimize database queries

### Useful Commands

```bash
# Restart app
az webapp restart --name foodxchange-app --resource-group foodxchange-rg

# Scale app
az appservice plan update --name foodxchange-plan --resource-group foodxchange-rg --sku S1

# View app settings
az webapp config appsettings list --name foodxchange-app --resource-group foodxchange-rg

# Update app settings
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings KEY=VALUE

# Delete app (if needed)
az webapp delete --name foodxchange-app --resource-group foodxchange-rg
```

## 💰 Cost Optimization

### Free Tier
- Use F1 (Free) App Service plan for development
- Limited to 1GB RAM and 60 minutes/day CPU time

### Production Recommendations
- B1 (Basic) plan: ~$13/month
- S1 (Standard) plan: ~$73/month
- Consider reserved instances for cost savings

### Monitoring Costs
- Application Insights: Free tier available
- Log Analytics: Pay per GB ingested

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit secrets to code
2. **HTTPS Only**: Enable HTTPS redirect
3. **Firewall Rules**: Restrict database access
4. **Managed Identity**: Use Azure AD for authentication
5. **Regular Updates**: Keep dependencies updated

## 📞 Support

- **Azure Documentation**: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
- **Azure CLI Reference**: [docs.microsoft.com/cli/azure](https://docs.microsoft.com/cli/azure)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

## 🎉 Congratulations!

Your FoodXchange application is now running on Azure! 

**Next Steps:**
1. Set up your production database
2. Configure monitoring and alerts
3. Set up your custom domain
4. Test all functionality
5. Set up backup and disaster recovery

Your application is now scalable, secure, and ready for production use! 🚀 