# Manual Azure Fix for FoodXchange

## 🔧 **Quick Fix Without Azure CLI**

Since Azure CLI is not installed, here's how to fix your Azure deployment manually:

### **Step 1: Access Azure Portal**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your App Service: `foodxchange-app`
3. Go to **Configuration** → **General settings**

### **Step 2: Update Startup Command**
In the **Startup Command** field, set:
```
gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app
```

### **Step 3: Set Environment Variables**
Go to **Configuration** → **Application settings** and add:

| Name | Value |
|------|-------|
| `DATABASE_URL` | `sqlite:///./foodxchange.db` |
| `SECRET_KEY` | `dev-secret-key-change-in-production` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `False` |

### **Step 4: Set Python Version**
In **Configuration** → **General settings**:
- **Stack**: Python
- **Major version**: 3.12
- **Minor version**: 3.12

### **Step 5: Restart the App**
1. Go to **Overview**
2. Click **Restart**
3. Wait 2-3 minutes for changes to take effect

### **Step 6: Test**
Visit your app: `http://www.fdx.trading/`
Health check: `http://www.fdx.trading/health`

## 🚀 **Alternative: Deploy via GitHub**

If manual fix doesn't work, you can deploy via GitHub:

1. **Push your fixed code to GitHub**
2. **In Azure Portal**:
   - Go to **Deployment Center**
   - Choose **GitHub** as source
   - Connect your repository
   - Deploy

## 📋 **What Was Fixed**

✅ **Missing Sentry files** - Created `sentry_config.py`, `sentry_optimized_config.py`, `sentry_middleware.py`

✅ **Wrong startup command** - Updated to use FastAPI app instead of WSGI

✅ **Environment variables** - Set proper database and app configuration

✅ **Python version** - Ensured Python 3.12 is used

## 🔍 **Troubleshooting**

If the app still doesn't work:

1. **Check logs**: Go to **Log stream** in Azure Portal
2. **Check health**: Visit `/health` endpoint
3. **Check system status**: Visit `/system-status` endpoint

## 📞 **Need Help?**

If you need assistance with the manual steps, I can guide you through each one or create a different deployment approach. 