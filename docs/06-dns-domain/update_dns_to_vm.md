# 🌐 Update fdx.trading to Point to Your VM

## Quick DNS Update (5 minutes)

### 1. **Find Your Domain Provider**
Your domain is registered with one of these:
- GoDaddy
- Namecheap  
- Google Domains
- Azure DNS
- Other registrar

### 2. **Update DNS Records**
Login to your domain provider and update:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 4.206.1.15 | 300 |
| A | www | 4.206.1.15 | 300 |

Remove or update the existing record pointing to 20.217.52.0

### 3. **Verify DNS Change**
```bash
# Check if update is complete (may take 5-30 mins)
nslookup fdx.trading

# Should show:
# Address: 4.206.1.15
```

### 4. **Set Up SSL on VM**
Once DNS is updated, run:
```bash
chmod +x setup_domain_ssl.sh
./setup_domain_ssl.sh
```

## Alternative: Use Azure Web App

If you prefer to keep using the Azure Web App:

### Cost Comparison:
- **VM Option**: $0/month (already running)
- **Web App Option**: +$20-50/month extra

### To deploy to Web App:
```bash
# Package your app
cd C:\Users\foodz\Desktop\FoodXchange
zip -r foodxchange.zip app.py templates static requirements.txt

# Deploy to Azure Web App
az webapp deployment source config-zip \
    --resource-group [YourResourceGroup] \
    --name [YourWebAppName] \
    --src foodxchange.zip
```

## 🎯 My Recommendation

Use your VM - it's already running, costs $0, and has everything set up. The Azure Web App would be redundant and cost extra.

Ready to update the DNS?