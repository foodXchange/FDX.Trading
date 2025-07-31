# 🌐 DNS Configuration Guide for fdx.trading

## The Problem
Your domain `www.fdx.trading` is showing `DNS_PROBE_FINISHED_NXDOMAIN` because the DNS records are not pointing to your Azure infrastructure.

## Quick Fix Options

### Option 1: Use Azure URL Temporarily
While setting up DNS, access your app directly:
```
https://YOUR_APP_NAME.azurewebsites.net
```

### Option 2: Configure DNS Properly (Recommended)

## 📋 DNS Configuration Steps

### Step 1: Find Your Azure App's IP Address
```powershell
# Get your app's IP address
az webapp show --name foodxchange-app --resource-group foodxchange-prod-rg --query outboundIpAddresses --output tsv
```

### Step 2: Configure DNS Records

You have two options for DNS configuration:

#### Option A: Use A Records (Direct IP)
Add these records in your domain provider's DNS settings:

```
Type: A
Name: @
Value: YOUR_AZURE_IP

Type: A  
Name: www
Value: YOUR_AZURE_IP
```

#### Option B: Use CNAME (Recommended)
```
Type: CNAME
Name: www
Value: YOUR_APP_NAME.azurewebsites.net

Type: A (for root domain)
Name: @  
Value: YOUR_AZURE_IP
```

### Step 3: Common Domain Providers

#### GoDaddy
1. Go to GoDaddy DNS Management
2. Add A record: @ → YOUR_AZURE_IP
3. Add A record: www → YOUR_AZURE_IP

#### Cloudflare
1. Go to Cloudflare DNS
2. Add A record: fdx.trading → YOUR_AZURE_IP
3. Add A record: www.fdx.trading → YOUR_AZURE_IP
4. Set proxy status to "DNS only" initially

#### Namecheap
1. Go to Advanced DNS
2. Add A record: @ → YOUR_AZURE_IP
3. Add A record: www → YOUR_AZURE_IP

#### Route 53 (AWS)
```bash
# Create A record for root domain
aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "fdx.trading",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "YOUR_AZURE_IP"}]
    }
  }]
}'
```

## 🚀 Complete Redeployment Commands

### Diagnose Current Issues
```powershell
# Check what's currently deployed
.\scripts\diagnose-deployment.ps1

# Check DNS resolution
nslookup www.fdx.trading
```

### Redeploy with Fix
```powershell
# Complete redeployment with DNS fix
.\scripts\redeploy-fix.ps1

# Or use free tier (no custom domain)
.\scripts\redeploy-fix.ps1 -UseFreeApp
```

### Add Custom Domain After DNS Propagation
```powershell
# Add custom domain (after DNS is configured)
az webapp config hostname add --webapp-name foodxchange-app --resource-group foodxchange-prod-rg --hostname www.fdx.trading

# Create SSL certificate
az webapp config ssl create --name foodxchange-app --resource-group foodxchange-prod-rg --hostname www.fdx.trading
```

## ⚡ Quick Alternative Solutions

### Solution 1: Use Azure's Free Tier Temporarily
```powershell
# Deploy to free tier (works immediately, no custom domain)
.\scripts\redeploy-fix.ps1 -UseFreeApp
```
Your app will be at: `https://foodxchange-app.azurewebsites.net`

### Solution 2: Use Subdomain
Instead of `www.fdx.trading`, use:
```
app.fdx.trading
foodxchange.fdx.trading
```

### Solution 3: Use Different Domain
If you have other domains available:
```powershell
.\scripts\redeploy-fix.ps1 -Domain "yourdomain.com"
```

## 🔧 Troubleshooting DNS Issues

### Check DNS Propagation
```bash
# Check if DNS has propagated globally
nslookup www.fdx.trading 8.8.8.8
nslookup www.fdx.trading 1.1.1.1

# Online tools
# https://www.whatsmydns.net/#A/www.fdx.trading
```

### Verify Azure Configuration
```powershell
# Check if custom hostname is added
az webapp config hostname list --webapp-name foodxchange-app --resource-group foodxchange-prod-rg

# Check app status
az webapp show --name foodxchange-app --resource-group foodxchange-prod-rg --query state
```

### Force DNS Refresh
```powershell
# Windows - flush DNS cache
ipconfig /flushdns

# Try different DNS servers
nslookup www.fdx.trading 8.8.8.8
```

## 📋 Immediate Action Plan

1. **Right Now - Quick Access:**
   ```powershell
   .\scripts\redeploy-fix.ps1 -UseFreeApp
   ```
   Your app will work immediately at the Azure URL.

2. **Configure DNS:**
   - Log into your domain provider
   - Add A records as shown above
   - Wait 5-30 minutes for propagation

3. **Upgrade to Custom Domain:**
   ```powershell
   # After DNS propagates
   az webapp config hostname add --webapp-name foodxchange-app --resource-group foodxchange-prod-rg --hostname www.fdx.trading
   ```

4. **Add SSL:**
   ```powershell
   az webapp config ssl create --name foodxchange-app --resource-group foodxchange-prod-rg --hostname www.fdx.trading
   ```

## 🎯 Recommended Quick Solution

**For immediate access:**
```powershell
.\scripts\redeploy-fix.ps1 -UseFreeApp
```

This will:
- ✅ Work immediately
- ✅ No DNS configuration needed
- ✅ Free to run
- ❌ No custom domain (but you can access your app)

**Your app will be live at:** `https://foodxchange-app.azurewebsites.net`

Once this works, you can configure DNS and upgrade to custom domain support later!