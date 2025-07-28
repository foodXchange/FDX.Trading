# FoodXchange Azure 503 Error Fix Guide

## Problem Summary
Your FoodXchange app at https://www.fdx.trading is showing a 503 error because:
1. The Azure App Service is not starting correctly
2. DNS may not be properly configured
3. The startup script may be failing to load dependencies
4. Health endpoint has been down for over 1 day

## Root Causes
1. **Startup Script Issues**: The current startup.py may be failing to import modules
2. **Missing Dependencies**: Critical packages might not be installed during deployment
3. **DNS Configuration**: The domain fdx.trading may not be properly pointing to Azure
4. **Python Path Issues**: The app directory might not be in the Python path
5. **Azure Configuration**: App Service settings may need adjustment

## Solution Steps

### Step 1: Run the Azure Deployment Fix (2-5 minutes)
```powershell
# Open PowerShell as Administrator and run:
.\fix_azure_503_error.ps1
```

This script will:
- Stop your App Service for clean deployment
- Update the startup configuration
- Create a fixed startup script with fallback options
- Configure proper Python settings
- Deploy the fixed application
- Restart the App Service

### Step 2: Verify DNS Configuration (5 minutes)
```powershell
# Run the DNS verification script:
.\verify_dns_and_fix.ps1
```

If DNS is not configured, add these records at your DNS provider:

**CNAME Record:**
- Host/Name: `www`
- Points to: `foodxchange.azurewebsites.net`
- TTL: 3600

**A Record:**
- Host/Name: `@` (or leave blank for root)
- Points to: `20.119.56.1`
- TTL: 3600

### Step 3: Quick Manual Fixes (if scripts fail)

#### Option A: Via Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your App Service (foodxchange)
3. Go to Configuration > General settings
4. Set:
   - Stack: Python
   - Version: 3.11
   - Startup Command: `python startup_fixed.py`
5. Save and restart

#### Option B: Via Azure CLI
```powershell
# Login to Azure
az login

# Update startup command
az webapp config set --resource-group foodxchange-rg --name foodxchange --startup-file "python startup_fixed.py"

# Restart the app
az webapp restart --resource-group foodxchange-rg --name foodxchange
```

### Step 4: Monitor the Fix (2-3 minutes)
```powershell
# Watch live logs
az webapp log tail --resource-group foodxchange-rg --name foodxchange
```

## Timeline
- **DNS Changes**: 5-30 minutes to propagate
- **App Service Restart**: 2-3 minutes
- **Full Deployment**: 5-10 minutes
- **Total Time to Fix**: 10-40 minutes (depending on DNS)

## Verification Steps
1. **Check Azure endpoint**: https://foodxchange.azurewebsites.net
2. **Check health endpoint**: https://foodxchange.azurewebsites.net/health
3. **Check custom domain**: https://www.fdx.trading
4. **Verify DNS**:
   ```powershell
   nslookup www.fdx.trading
   ```

## What the Fix Does
1. **Creates startup_fixed.py**: A robust startup script with:
   - Automatic package installation for missing dependencies
   - Proper path configuration
   - Fallback app if main app fails
   - Better error logging

2. **Updates web.config**: 
   - Increases startup timeout to 300 seconds
   - Enables proper logging
   - Sets correct Python handler

3. **Configures Azure Settings**:
   - Enables build during deployment
   - Sets correct Python version
   - Configures proper ports
   - Enables application storage

## If Still Not Working
1. **Check Logs**:
   ```powershell
   # Download recent logs
   az webapp log download --resource-group foodxchange-rg --name foodxchange --log-file logs.zip
   ```

2. **Check App Service Health**:
   ```powershell
   az webapp show --resource-group foodxchange-rg --name foodxchange --query state
   ```

3. **Force Rebuild**:
   ```powershell
   # Clear cache and rebuild
   az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange --src foodxchange_fixed_deployment.zip --clean true
   ```

## Common Issues and Solutions

### Issue: "Module not found" errors
**Solution**: The startup_fixed.py script automatically installs missing packages

### Issue: DNS not resolving
**Solution**: Wait 30 minutes for propagation, or use Google DNS (8.8.8.8)

### Issue: SSL certificate errors
**Solution**: Azure provides free SSL certificates - enable in Custom domains section

### Issue: App starts but crashes immediately
**Solution**: Check environment variables are set correctly in Azure Portal

## Support Contacts
- Azure Support: https://azure.microsoft.com/support
- Check Azure Service Health: https://status.azure.com
- DNS Propagation Checker: https://dnschecker.org

## Success Indicators
- ✅ https://foodxchange.azurewebsites.net returns 200 OK
- ✅ https://www.fdx.trading loads the application
- ✅ /health endpoint returns {"status": "healthy"}
- ✅ No errors in application logs