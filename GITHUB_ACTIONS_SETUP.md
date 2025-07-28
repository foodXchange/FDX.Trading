# GitHub Actions + Azure Deployment Setup

## 🚀 **Your New Workflow: GitHub → Azure**

Instead of manual deployment, you'll now have **automatic deployment** when you push to GitHub!

## 📋 **Setup Steps**

### **Step 1: Create Azure Web App (if not exists)**

```bash
# Create resource group
az group create --name foodxchange-rg --location "East US"

# Create app service plan
az appservice plan create --name foodxchange-plan --resource-group foodxchange-rg --sku B1 --is-linux

# Create web app
az webapp create --name foodxchange-app --resource-group foodxchange-rg --plan foodxchange-plan --runtime "PYTHON|3.12"
```

### **Step 2: Get Azure Publish Profile**

```bash
# Get the publish profile
az webapp deployment list-publishing-profiles --name foodxchange-app --resource-group foodxchange-rg --xml
```

**Copy the entire XML output** - you'll need this for GitHub secrets.

### **Step 3: Set Up GitHub Secrets**

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add this secret:
   - **Name**: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Value**: Paste the XML from Step 2

### **Step 4: Configure Azure App Settings**

```bash
# Set environment variables in Azure
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true \
  PYTHON_VERSION=3.12 \
  WEBSITES_PORT=8000 \
  ENVIRONMENT=production \
  DEBUG=False

# Set your database connection (replace with your actual connection string)
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  DATABASE_URL="your-database-connection-string"

# Set your secret key
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  SECRET_KEY="your-production-secret-key"
```

## 🔄 **Your New Development Workflow**

### **Local Development (Same as Before)**
```bash
# Start local development
start-local.bat
```

### **Deploy to Azure (Now Automatic!)**
```bash
# Just push to GitHub!
git add .
git commit -m "Update feature"
git push origin main
```

**What happens:**
1. ✅ GitHub Actions automatically triggers
2. ✅ Builds your application
3. ✅ Deploys to Azure
4. ✅ Your app is live at `https://foodxchange-app.azurewebsites.net`

## 📊 **Workflow Comparison**

| Method | Local Development | Azure Deployment |
|--------|------------------|------------------|
| **Before** | `start-local.bat` | `quick-deploy.bat` |
| **Now** | `start-local.bat` | `git push origin main` |

## 🎯 **Benefits**

- ✅ **Automatic deployment** - No manual steps
- ✅ **Same local experience** - Keep using Cursor
- ✅ **Version control** - Every push is tracked
- ✅ **Rollback capability** - Easy to revert changes
- ✅ **Lean workflow** - Minimal friction

## 🛠️ **Quick Setup Commands**

### **One-time setup:**
```bash
# 1. Create Azure resources
az group create --name foodxchange-rg --location "East US"
az appservice plan create --name foodxchange-plan --resource-group foodxchange-rg --sku B1 --is-linux
az webapp create --name foodxchange-app --resource-group foodxchange-rg --plan foodxchange-plan --runtime "PYTHON|3.12"

# 2. Get publish profile
az webapp deployment list-publishing-profiles --name foodxchange-app --resource-group foodxchange-rg --xml

# 3. Configure app settings
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true PYTHON_VERSION=3.12 WEBSITES_PORT=8000
```

### **Daily workflow:**
```bash
# 1. Develop locally
start-local.bat

# 2. Deploy to Azure
git add .
git commit -m "Your changes"
git push origin main
```

## 🔍 **Monitoring**

### **Check GitHub Actions:**
- Go to your GitHub repository
- Click **Actions** tab
- See deployment status

### **Check Azure:**
```bash
# View app status
az webapp show --name foodxchange-app --resource-group foodxchange-rg

# View logs
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg
```

## 🎉 **You're All Set!**

Your development workflow is now:
1. **Develop locally** in Cursor (same as before)
2. **Push to GitHub** (automatic Azure deployment)
3. **Your app is live** on Azure

**No more manual deployment steps!** 🚀 