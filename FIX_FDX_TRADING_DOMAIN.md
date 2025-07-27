# Fix fdx-trading.com Domain Issues

## Current Problems:
1. **DNS not configured**: fdx-trading.com and www.fdx-trading.com are not resolving
2. **Azure app down**: foodxchange-app.azurewebsites.net returns 503 error

## Solution Steps:

### Step 1: Configure DNS in Namecheap
You need to add DNS records in your Namecheap account:

1. **Login to Namecheap.com**
2. **Go to Domain List → fdx.trading → Manage**
3. **Click "Advanced DNS" tab**
4. **Add these records:**

```
Type: CNAME
Host: @
Value: foodxchange-app.azurewebsites.net
TTL: Automatic

Type: CNAME
Host: www
Value: foodxchange-app.azurewebsites.net
TTL: Automatic
```

**Alternative (if CNAME @ doesn't work):**
```
Type: A
Host: @
Value: 20.50.160.212
TTL: Automatic

Type: CNAME
Host: www
Value: fdx.trading
TTL: Automatic
```

### Step 2: Fix Azure App Service
The app is currently down (503 error). To fix:

1. **Check deployment status**:
   ```bash
   az webapp log deployment show --name foodxchange-app --resource-group foodxchange-rg
   ```

2. **Restart the app**:
   ```bash
   az webapp restart --name foodxchange-app --resource-group foodxchange-rg
   ```

3. **Check logs**:
   ```bash
   az webapp log tail --name foodxchange-app --resource-group foodxchange-rg
   ```

### Step 3: Deploy Latest Code
Since we fixed the configuration issues earlier:

```bash
# Commit and push changes
git add .
git commit -m "Fix Azure deployment configuration"
git push origin main
```

### Step 4: Verify Setup
After DNS propagation (15-60 minutes):

1. **Check DNS**: https://whatsmydns.net
2. **Test Azure URL**: https://foodxchange-app.azurewebsites.net
3. **Test domain**: https://fdx.trading
4. **Test www**: https://www.fdx-trading.com

## Quick Actions Needed:

1. **NOW**: Configure DNS in Namecheap (takes 2 minutes)
2. **NOW**: Restart Azure app service
3. **WAIT**: 15-60 minutes for DNS propagation
4. **TEST**: Verify both domains work

## Expected Result:
- fdx.trading → Your FoodXchange app
- www.fdx-trading.com → Your FoodXchange app
- Both with HTTPS/SSL enabled