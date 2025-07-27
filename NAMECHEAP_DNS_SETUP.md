# Namecheap DNS Setup for fdx.trading

## ✅ Azure Configuration Complete!

Your Azure App Service has been successfully configured with:
- ✅ Custom domain: `fdx.trading`
- ✅ WWW subdomain: `www.fdx.trading`
- ✅ SSL certificates: Automatically provisioned
- ✅ HTTPS enforcement: Enabled

## 🚀 Quick DNS Setup (Recommended)

### Option A: Simple CNAME Setup (Easiest)

1. **Login to Namecheap** and go to your domain `fdx.trading`
2. **Go to "Advanced DNS"** section
3. **Add these DNS records:**

```
Type: CNAME
Name: @
Value: foodxchange-app.azurewebsites.net
TTL: Automatic

Type: CNAME  
Name: www
Value: foodxchange-app.azurewebsites.net
TTL: Automatic
```

### Option B: A Record Setup (Better Performance)

If you prefer A records, use these IP addresses:

```
Type: A
Name: @
Value: 20.50.160.212
TTL: Automatic

Type: A
Name: @
Value: 20.50.161.0
TTL: Automatic

Type: A
Name: @
Value: 51.105.187.123
TTL: Automatic

Type: CNAME
Name: www
Value: fdx.trading
TTL: Automatic
```

## 📋 Step-by-Step Instructions

### Step 1: Access Namecheap DNS
1. Go to [namecheap.com](https://namecheap.com) and login
2. Click "Domain List" 
3. Find `fdx.trading` and click "Manage"
4. Click "Advanced DNS" tab

### Step 2: Remove Existing Records
- Delete any existing A or CNAME records for `@` or `www`
- Keep email records (MX, TXT) if you use email

### Step 3: Add New Records
- Add the records from Option A or B above
- Click "Save All Changes"

### Step 4: Wait for Propagation
- DNS changes take 15 minutes to 48 hours
- You can check propagation at [whatsmydns.net](https://whatsmydns.net)

## 🧪 Testing Your Domain

After DNS propagation, test these URLs:

- ✅ **Main domain**: https://fdx.trading
- ✅ **WWW domain**: https://www.fdx.trading
- ✅ **Azure URL**: https://foodxchange-app.azurewebsites.net
- ✅ **Health check**: https://fdx.trading/health
- ✅ **System status**: https://fdx.trading/system-status

## 🔒 SSL Certificate Status

Your SSL certificates are already provisioned:
- `fdx.trading`: ✅ Active (Thumbprint: 324EEC5379180D8FB9D39AB39C1CDEB97EA1134D)
- `www.fdx.trading`: ✅ Active (Thumbprint: 5507CE09129932943EFBB83D231590E8675B5A45)

## 🚨 Important Notes

1. **Use Option A (CNAME)** if you want the simplest setup
2. **Use Option B (A Records)** if you want better performance
3. **Don't mix A and CNAME records** for the same hostname
4. **Wait for DNS propagation** before testing
5. **SSL certificates are automatic** - no manual setup needed

## 🔧 Troubleshooting

### If domain doesn't work:
1. **Check DNS propagation**: [whatsmydns.net](https://whatsmydns.net)
2. **Verify records are correct** in Namecheap
3. **Wait longer** - DNS can take up to 48 hours
4. **Check Azure status**: https://foodxchange-app.azurewebsites.net

### If SSL doesn't work:
1. **Wait 5-10 minutes** for certificate provisioning
2. **Check Azure App Service** → Custom domains → SSL bindings
3. **Clear browser cache** and try again

## 📞 Support

- **DNS Issues**: Contact Namecheap support
- **Azure Issues**: Check Azure App Service logs
- **Domain Issues**: Test with Azure URL first

## 🎯 Next Steps

1. **Configure DNS records** in Namecheap (see above)
2. **Wait for propagation** (15-60 minutes)
3. **Test your domain**: https://fdx.trading
4. **Set up monitoring** for uptime
5. **Update internal links** to use fdx.trading 