# Fast Deployment from Cursor IDE

## Fastest Method: Direct File Deploy (10-30 seconds)

### Option 1: Using Azure CLI (Recommended)
```powershell
# One command to deploy (run from FoodXchange folder)
az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange-app --src deploy.zip

# Or use the PowerShell script
.\deploy.ps1
```

### Option 2: Using Kudu Console (Instant)
1. Go to: https://foodxchange-app.scm.azurewebsites.net/DebugConsole
2. Navigate to: `/home/site/wwwroot`
3. Drag and drop your files directly
4. Changes are instant!

### Option 3: Using FTP (30 seconds)
1. Get FTP credentials from Azure Portal
2. Use FileZilla or Windows Explorer
3. Connect to: `ftps://foodxchange-app.ftp.azurewebsites.windows.net`
4. Upload only changed files

## Current Issue
The app is showing Application Error. To fix:
1. Go to Kudu Console
2. Check `/home/LogFiles/` for errors
3. The issue might be that Python can't find the files

## Quick Fix Commands
```bash
# Check what's deployed
az webapp show --resource-group foodxchange-rg --name foodxchange-app --query "siteConfig.appCommandLine"

# Deploy single file
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path index.py --target-path /site/wwwroot/index.py --type static
```