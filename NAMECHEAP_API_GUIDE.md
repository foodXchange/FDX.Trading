# Namecheap API Setup Guide

## 🚀 Getting Your API Credentials

### Step 1: Enable API Access
1. **Login** to your Namecheap account
2. **Navigate** to: Profile → Tools → Namecheap API access
3. **Enable** API access if not already enabled
4. **Whitelist** your IP address: `95.35.178.122`

### Step 2: Get Your API Key
1. On the API access page, find your **API Key**
2. If you don't have one, click **Generate** or **Regenerate**
3. **Copy** the API key (it's a long string)

### Step 3: Update Configuration
Edit the file: `C:\Users\foodz\.namecheap-api\config.json`

Replace:
- `YOUR_NAMECHEAP_USERNAME` → Your actual Namecheap username
- `YOUR_NAMECHEAP_API_KEY` → The API key from Step 2

### Step 4: Run the Update
```bash
python update_dns.py
```

## 📋 Current Configuration Template
```json
{
  "username": "YOUR_NAMECHEAP_USERNAME",
  "api_key": "YOUR_NAMECHEAP_API_KEY", 
  "api_user": "YOUR_NAMECHEAP_USERNAME",
  "client_ip": "95.35.178.122"
}
```

## 🔧 Alternative: Manual DNS Update
If API setup is difficult, you can still update DNS manually:

**CNAME Record:**
- Type: `CNAME`
- Host: `www`
- Target: `foodxchange-deploy-app.azurewebsites.net`

**TXT Record:**
- Type: `TXT`
- Host: `asuid.www`
- Value: `41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77`

## 📊 Monitor Progress
```bash
python check_dns_clean.py
```

## ❓ Troubleshooting
- **API Access Denied**: Make sure your IP `95.35.178.122` is whitelisted
- **Invalid Credentials**: Double-check username and API key
- **Domain Not Found**: Verify you own `fdx.trading` in this Namecheap account