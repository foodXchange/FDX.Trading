# Azure Auto-Fix Dashboard

## 🚀 Quick Start

### 1. Deploy Minimal Working App
```cmd
deploy.cmd
```
This deploys a minimal FastAPI app that will respond to health checks.

### 2. Run Full Diagnostic & Fix
```cmd
python azure_auto_fixer.py
```
This will:
- Check app health
- Analyze logs for errors
- Fix configuration issues
- Update dependencies
- Apply all necessary fixes

### 3. Start Continuous Monitoring
```cmd
start_monitor.cmd
```
This runs 24/7 and:
- Monitors app health every 60 seconds
- Auto-restarts on crashes
- Scales up on memory issues
- Sends notifications

## 📊 Current Status

### App Details
- **Name**: foodxchange-app
- **URL**: https://foodxchange-app.azurewebsites.net
- **Resource Group**: foodxchange-rg
- **Runtime**: Python 3.12

### Common Issues & Auto-Fixes

| Issue | Symptom | Auto-Fix Applied |
|-------|---------|------------------|
| Module Not Found | `ModuleNotFoundError` in logs | Updates requirements.txt |
| Virtual Env Not Active | Dependencies installed but not found | Sets proper startup command |
| Memory Issues | `MemoryError` or crashes | Scales up to P1V2 temporarily |
| App Not Starting | 503 Service Unavailable | Restarts app service |
| Config Missing | Missing Azure settings | Adds required app settings |

## 🛠️ Manual Commands

### Check App Status
```bash
az webapp show --name foodxchange-app --resource-group foodxchange-rg
```

### View Live Logs
```bash
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg
```

### Restart App
```bash
az webapp restart --name foodxchange-app --resource-group foodxchange-rg
```

### Deploy Your Full App
```bash
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path your-app.zip --type zip
```

## 📝 Files Created

1. **azure_auto_fixer.py** - Comprehensive diagnostic and fix tool
2. **azure_continuous_monitor.py** - 24/7 monitoring system
3. **azure_quick_fix.zip** - Minimal working deployment
4. **deploy.cmd** - Quick deployment script
5. **start_monitor.cmd** - Start monitoring script

## 🔍 Troubleshooting

### If deployment fails:
1. Check Azure CLI is logged in: `az account show`
2. Verify resource names are correct
3. Check subscription: `az account list`

### If app still shows 503:
1. Run the auto-fixer: `python azure_auto_fixer.py`
2. Check Kudu console: https://foodxchange-app.scm.azurewebsites.net
3. Review deployment logs in `azure_auto_fixer.log`

### If monitor crashes:
1. Check `azure_monitor.log` for errors
2. Ensure Python packages are installed: `pip install aiohttp`
3. Verify Azure CLI credentials

## 📈 Next Steps

1. **Deploy your actual application** once the minimal app is working
2. **Configure environment variables** for your database, APIs, etc.
3. **Set up custom domain** if needed
4. **Enable Application Insights** for better monitoring

## 🚨 Emergency Contacts

- Azure Support: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- Kudu Console: https://foodxchange-app.scm.azurewebsites.net
- Azure Portal: https://portal.azure.com