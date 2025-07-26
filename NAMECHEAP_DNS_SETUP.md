# Namecheap DNS Configuration for fdx.trading

## Quick Setup Guide

### Step 1: Login to Namecheap
1. Go to [Namecheap.com](https://namecheap.com)
2. Click "Sign In" and login to your account
3. Go to "Domain List" and find `fdx.trading`

### Step 2: Access DNS Settings
1. Click on the "Manage" button next to `fdx.trading`
2. Go to the "Advanced DNS" tab
3. You'll see a list of existing DNS records

### Step 3: Configure DNS Records

#### Option A: CNAME Records (Easiest - Recommended)

**Record 1: Main Domain**
```
Type: CNAME Record
Host: @
Value: foodxchange-app.azurewebsites.net
TTL: Automatic
```

**Record 2: WWW Subdomain**
```
Type: CNAME Record
Host: www
Value: foodxchange-app.azurewebsites.net
TTL: Automatic
```

#### Option B: A Records (Better Performance)

**Record 1: Main Domain**
```
Type: A Record
Host: @
Value: 20.50.160.212
TTL: Automatic
```

**Record 2: WWW Subdomain**
```
Type: CNAME Record
Host: www
Value: fdx.trading
TTL: Automatic
```

### Step 4: Save Changes
1. Click "Save All Changes" at the bottom
2. Wait for DNS propagation (15 minutes to 48 hours)

## DNS Propagation Check

After setting up DNS records, you can check propagation:

1. **Online Tools:**
   - [whatsmydns.net](https://www.whatsmydns.net/) - Enter `fdx.trading`
   - [dnschecker.org](https://dnschecker.org/) - Enter `fdx.trading`

2. **Command Line:**
   ```bash
   nslookup fdx.trading
   nslookup www.fdx.trading
   ```

## Expected Results

After DNS propagation, you should see:
- `fdx.trading` resolves to `foodxchange-app.azurewebsites.net`
- `www.fdx.trading` resolves to `foodxchange-app.azurewebsites.net`

## Troubleshooting

### If DNS doesn't work after 24 hours:

1. **Check record format:**
   - Make sure there are no extra spaces
   - Ensure the value is exactly `foodxchange-app.azurewebsites.net`

2. **Try A records instead:**
   - Use the IP addresses provided above
   - A records can be faster than CNAME

3. **Contact Namecheap support:**
   - If you're still having issues after 48 hours

### Common Issues:

1. **"CNAME record already exists"**
   - Remove any existing A or CNAME records for `@` and `www`
   - Then add the new records

2. **"Invalid hostname"**
   - Make sure you're using the correct Azure App Service name
   - Check for typos in `foodxchange-app.azurewebsites.net`

## Next Steps After DNS Setup

1. **Run the Azure setup script:**
   ```powershell
   .\setup_custom_domain.ps1
   ```

2. **Test the domain:**
   - Visit https://fdx.trading
   - Visit https://www.fdx.trading

3. **Set up SSL certificate** in Azure Portal

4. **Update your application** to use the new domain

## Azure App Service Details

- **App Service Name:** foodxchange-app
- **Resource Group:** foodxchange-rg
- **Current URL:** https://foodxchange-app.azurewebsites.net
- **Target URL:** https://fdx.trading

## Support

If you need help:
1. **Namecheap Support:** [support.namecheap.com](https://support.namecheap.com)
2. **Azure Support:** [portal.azure.com](https://portal.azure.com) → Help + Support
3. **DNS Propagation:** [whatsmydns.net](https://www.whatsmydns.net/) 