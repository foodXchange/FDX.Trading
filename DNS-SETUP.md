# DNS Configuration for fdx.trading → Azure Deployment

## Required DNS Records

### 1. Domain Verification TXT Record
Add this TXT record to your DNS provider:

```
Name: asuid.www.fdx.trading
Type: TXT
Value: 41260BF0BFCF0F62C6509763F8D3773DCEB6E1DF952696707F2B337DA93EEC77
TTL: 300
```

### 2. CNAME Record for www subdomain
```
Name: www
Type: CNAME
Value: foodxchange-deploy-app.azurewebsites.net
TTL: 300
```

### 3. A Record for root domain (optional)
If you want fdx.trading (without www) to work:
```
Name: @
Type: A
Value: [Get IP from Azure Web App]
TTL: 300
```

## Steps to Configure

1. **Add TXT Record**: Add the domain verification record first
2. **Wait 5-10 minutes** for DNS propagation
3. **Deploy the application** (GitHub Actions will configure the domain)
4. **Add CNAME record** after successful deployment
5. **Test**: https://www.fdx.trading should show your FoodXchange app

## Current Azure Resources

- **Web App**: foodxchange-deploy-app.azurewebsites.net
- **Container Registry**: foodxchangeacr2025deploy.azurecr.io
- **Resource Group**: foodxchange-deploy
- **Location**: West Europe

## Production Features

✅ **ONLY FoodXchange App** (port 9000)  
✅ **No pgAdmin** (secure production setup)  
✅ **No Redis Commander** (no admin tools exposed)  
✅ **No MailHog** (production email service)  
✅ **SQLite database** (can upgrade to PostgreSQL later)  
✅ **SSL/HTTPS** automatic via Azure  
✅ **Custom domain** support for fdx.trading  

This is a clean, secure, production-ready deployment!