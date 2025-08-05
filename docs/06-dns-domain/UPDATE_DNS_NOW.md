# 🚀 Update fdx.trading DNS - Quick Steps

## Your Domain Info:
- **Current IP**: 20.217.52.0 (Azure Web App - empty)
- **New IP**: 4.206.1.15 (Your VM - app running)
- **Registrar**: Likely Namecheap (registrar-servers.com)

## 📋 Steps to Update DNS (5 minutes):

### 1. Login to Namecheap
Go to: https://www.namecheap.com
Login to your account

### 2. Find Your Domain
- Click "Domain List" 
- Find "fdx.trading"
- Click "Manage"

### 3. Update DNS Records
Click "Advanced DNS" tab and update:

**Delete/Edit these old records:**
- A Record @ → 20.217.52.0 (DELETE or EDIT)
- A Record www → 20.217.52.0 (DELETE or EDIT)

**Add/Update to these:**
| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | 4.206.1.15 | Automatic |
| A Record | www | 4.206.1.15 | Automatic |

### 4. Save Changes
Click "Save Changes" ✓

## 🔍 Verify DNS Update:

Run this command every few minutes:
```bash
nslookup fdx.trading
```

When it shows `Address: 4.206.1.15`, the DNS has updated!

## 🔒 After DNS Updates (10-30 mins):

Run this to set up SSL:
```bash
chmod +x setup_domain_ssl.sh
./setup_domain_ssl.sh
```

## 📱 Quick Check:
Once DNS updates, visit:
- http://fdx.trading
- http://www.fdx.trading

You should see your login page!

---
**Need help?** The DNS update usually takes 5-30 minutes to propagate worldwide.