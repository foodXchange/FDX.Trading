# 🚀 FoodXchange Azure Deployment Quick Start

## 📋 What You'll Get
- ✅ Complete audit of existing Azure resources
- ✅ Safe cleanup of old resources
- ✅ Fresh deployment to fdx.trading
- ✅ All configurations automated

## 🔧 Prerequisites

Install required tools:
```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Install GitHub CLI (optional but recommended)
winget install GitHub.cli

# Docker Desktop - download from https://www.docker.com/products/docker-desktop
```

## 🚀 Quick Deployment (3 Steps)

### Step 1: Audit What Exists
```powershell
# See what's currently in Azure (safe, read-only)
.\scripts\audit-and-deploy.ps1 -AuditOnly
```

### Step 2: Clean and Deploy
```powershell
# Run complete cleanup and fresh deployment
.\scripts\audit-and-deploy.ps1

# Or force without prompts (BE CAREFUL!)
.\scripts\audit-and-deploy.ps1 -Force
```

### Step 3: Configure Your Secrets
After deployment completes, add your Azure AI credentials:

```powershell
# Set your Azure OpenAI credentials
az webapp config appsettings set `
  --name foodxchange-app `
  --resource-group foodxchange-prod-rg `
  --settings `
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" `
    AZURE_OPENAI_KEY="your-key-here" `
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
```

## 📊 Individual Commands Reference

### Just Audit (No Changes)
```powershell
# List all Azure resources
.\scripts\cleanup-azure.ps1 -DryRun

# Check GitHub repository
.\scripts\cleanup-github.sh
```

### Just Cleanup
```powershell
# Clean Azure only
.\scripts\cleanup-azure.ps1

# Clean GitHub only
.\scripts\cleanup-github.sh
```

### Just Deploy
```powershell
# Fresh deployment only (no cleanup)
.\scripts\fresh-deploy.ps1 -SkipCleanup
```

## 🔍 Monitoring Your Deployment

### Check Status
```powershell
# View deployment logs
az webapp log tail --name foodxchange-app --resource-group foodxchange-prod-rg

# Check health
curl https://www.fdx.trading/health
```

### View Resources
```powershell
# List all resources
az resource list --resource-group foodxchange-prod-rg -o table

# Open Azure Portal
start https://portal.azure.com
```

## ⚠️ Important Notes

1. **DNS Configuration**: After deployment, update your domain's DNS:
   - Point A records for fdx.trading to the provided IP
   - Or use CNAME to point to your-app.azurewebsites.net

2. **SSL Certificates**: Run this after DNS propagates:
   ```powershell
   az webapp config ssl create --name foodxchange-app --resource-group foodxchange-prod-rg --hostname www.fdx.trading
   ```

3. **Credentials**: The script saves credentials to `deployment-credentials.txt`
   - **Store them securely**
   - **Delete the file immediately**

## 🆘 Troubleshooting

### If deployment fails:
```powershell
# Check logs
az webapp log tail --name foodxchange-app --resource-group foodxchange-prod-rg

# Restart app
az webapp restart --name foodxchange-app --resource-group foodxchange-prod-rg
```

### If cleanup fails:
```powershell
# Manual cleanup of specific resource
az group delete --name OLD_RESOURCE_GROUP --yes

# Force delete stuck resources
az resource delete --ids /subscriptions/xxx/resourceGroups/xxx/providers/xxx
```

## 📱 GitHub Actions Setup

After deployment, set up CI/CD:

```powershell
# Set GitHub secrets from deployment
gh secret set AZURE_WEBAPP_NAME --body "foodxchange-app"
gh secret set AZURE_REGISTRY_URL --body "foodxchangeacr.azurecr.io"
gh secret set DATABASE_URL --body "your-connection-string"
# ... (script provides all needed values)
```

## ✅ Verification Checklist

After deployment:
- [ ] Website loads at https://www.fdx.trading
- [ ] Health endpoint returns 200: https://www.fdx.trading/health
- [ ] SSL certificate is valid
- [ ] Database connection works
- [ ] Redis cache is functional
- [ ] File uploads work
- [ ] AI services integrated

---

## 🎯 One Command Deployment

**For the brave** (does everything automatically):
```powershell
.\scripts\audit-and-deploy.ps1 -Force -ResourceGroupName "foodxchange-prod-rg" -Location "eastus" -Domain "fdx.trading"
```

Good luck! 🚀