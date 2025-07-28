# Azure App Service Deployment Fix Guide

## Problem Summary

Your Azure App Service (fdx-trading.azurewebsites.net) is experiencing deployment issues where the Python dependencies are not being found at runtime, resulting in `ModuleNotFoundError` for packages like `fastapi`, `uvicorn`, and `sentry_sdk`.

## Root Causes

1. **Virtual Environment Not Activated**: The `antenv` virtual environment created by Oryx during deployment is not being properly activated at runtime
2. **Conflicting Startup Configurations**: Multiple startup files (web.config, startup.sh, azure_startup.py) with different commands
3. **Module Import Errors**: Python cannot find installed packages because it's not looking in the virtual environment's site-packages directory
4. **HEAD Request Handling**: The app returns 405 Method Not Allowed for HEAD requests used by Azure health checks

## Solution Steps

### 1. Quick Fix - Deploy Minimal Working App (2 minutes)

Run the automated fix script I've created:

```powershell
# Step 1: Create minimal deployment package
powershell -ExecutionPolicy Bypass -File azure_deploy_fix.ps1

# Step 2: Deploy to Azure (requires Azure CLI)
powershell -ExecutionPolicy Bypass -File deploy_to_azure.ps1
```

### 2. Manual Fix via Azure Portal (5 minutes)

If you prefer using the Azure Portal:

1. **Navigate to your App Service**
   - Go to https://portal.azure.com
   - Find "fdx-trading" in App Services

2. **Update Configuration Settings**
   - Go to Configuration → Application settings
   - Add/Update these settings:
     ```
     SCM_DO_BUILD_DURING_DEPLOYMENT = true
     ENABLE_ORYX_BUILD = true
     PYTHON_ENABLE_GUNICORN_MULTIWORKERS = false
     WEBSITES_PORT = 8000
     WEBSITE_HEALTHCHECK_MAXPINGFAILURES = 10
     ```

3. **Set Startup Command**
   - Go to Configuration → General settings
   - Set Startup Command to: `python -m uvicorn app:app --host 0.0.0.0 --port 8000`

4. **Deploy the Minimal App**
   - Go to Deployment Center
   - Choose "Local Git" or drag-and-drop the `azure_fix_deployment.zip` file

### 3. Comprehensive Diagnostic and Fix (Python Script)

Run the diagnostic script that will automatically detect and fix issues:

```bash
python azure_diagnostic_fix.py fdx-trading foodxchange-rg
```

This script will:
- Check Azure CLI and login status
- Verify app existence and configuration
- Fix app settings
- Create and deploy a minimal working app
- Test all endpoints

## DNS Configuration (If Needed)

If you're setting up a custom domain:

**For fdx-trading.com:**
- Type: CNAME
- Host: www
- Points to: fdx-trading.azurewebsites.net
- TTL: 3600

**For root domain:**
- Type: A
- Host: @
- Points to: Azure App Service IP (found in Custom domains)
- TTL: 3600

## Timeline

- **Deployment**: 2-5 minutes
- **App Startup**: 30-60 seconds
- **DNS Propagation**: 5 minutes to 48 hours (usually under 1 hour)

## Verification

After deployment, test these endpoints:

1. **Health Check**: https://fdx-trading.azurewebsites.net/health
   - Expected: `{"status": "healthy", "timestamp": "..."}`

2. **Root Endpoint**: https://fdx-trading.azurewebsites.net/
   - Expected: `{"message": "FoodXchange API", "version": "1.0.0", ...}`

3. **API Documentation**: https://fdx-trading.azurewebsites.net/docs
   - Expected: FastAPI automatic documentation

## Common Issues and Solutions

### Issue: "ModuleNotFoundError"
**Solution**: Ensure `SCM_DO_BUILD_DURING_DEPLOYMENT=true` and redeploy

### Issue: "503 Service Unavailable"
**Solution**: Check startup command and ensure it uses the correct Python path

### Issue: "Container failed to start"
**Solution**: Use the minimal deployment first, then gradually add complexity

### Issue: "HEAD requests return 405"
**Solution**: The minimal app includes HEAD endpoint handlers

## Monitoring

Check deployment logs:
```bash
az webapp log tail --name fdx-trading --resource-group foodxchange-rg
```

View Kudu console:
- https://fdx-trading.scm.azurewebsites.net

## Next Steps

Once the minimal app is working:

1. **Add Dependencies Gradually**: Update requirements.txt with needed packages
2. **Test Locally**: Ensure your full app works with `uvicorn app:app`
3. **Deploy Full App**: Replace the minimal app with your complete application
4. **Set Environment Variables**: Add any required configuration via App Settings
5. **Configure Database**: Set up connection strings if using Azure PostgreSQL

## Support Commands

```bash
# Check app status
az webapp show --name fdx-trading --resource-group foodxchange-rg --query state

# View recent logs
az webapp log download --name fdx-trading --resource-group foodxchange-rg

# Restart app
az webapp restart --name fdx-trading --resource-group foodxchange-rg

# SSH into container (for debugging)
az webapp ssh --name fdx-trading --resource-group foodxchange-rg
```

## Contact

If issues persist after following this guide, the logs from the Kudu console will provide more specific error details to investigate.