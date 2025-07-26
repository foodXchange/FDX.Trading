# Azure PostgreSQL Setup Guide

## Connection Issue: Firewall Configuration Required

The connection test failed with a timeout error, which means your Azure PostgreSQL server is not accepting connections from your current IP address.

## Steps to Fix:

### 1. Configure Firewall Rules in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your PostgreSQL server: **foodxchangepgfr**
3. In the left menu, find **Settings** → **Connection security**
4. Add a firewall rule:
   - Rule name: `LocalDevelopment`
   - Start IP: Your current IP address
   - End IP: Your current IP address
   - Click **Save**

To find your current IP address:
- Visit: https://whatismyipaddress.com/
- Or run in PowerShell: `(Invoke-WebRequest -uri "https://api.ipify.org").Content`

### 2. Alternative: Allow All Azure Services

In the same Connection security page:
- Toggle **Allow access to Azure services** to **ON**
- This allows connections from any Azure service

### 3. Verify SSL Mode

Your connection string already includes `?sslmode=require` which is correct for Azure PostgreSQL.

## Connection String Formats

### Format 1 (Standard):
```
postgresql://foodxchangedbadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange?sslmode=require
```

### Format 2 (URL-encoded username):
```
postgresql://foodxchangedbadmin%40foodxchangepgfr:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange?sslmode=require
```

## Test Connection After Firewall Update

After updating the firewall rules, wait 1-2 minutes, then run:
```bash
python test_db_simple.py
```

## Create Database (if needed)

If the connection works but the database doesn't exist, you'll need to create it:

1. Connect to the `postgres` database first
2. Run: `CREATE DATABASE foodxchange;`

## Next Steps After Connection Success

1. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

2. **Start Application**:
   ```bash
   python azure_startup.py
   ```

## Troubleshooting

If you still can't connect:

1. **Check server status**: Ensure the PostgreSQL server is in "Ready" state in Azure Portal
2. **Verify credentials**: Double-check username and password
3. **Check network**: Ensure you're not behind a corporate firewall blocking port 5432
4. **Try Azure Cloud Shell**: As a last resort, use Azure Cloud Shell which bypasses firewall issues

## Security Notes

- The `.env` file contains sensitive credentials - never commit it to Git
- Use the `.env.example` file as a template for other developers
- Consider using Azure Key Vault for production credentials