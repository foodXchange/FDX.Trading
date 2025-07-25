# Azure PostgreSQL Connection Fix Guide

## Current Issue
Connection timeout when trying to connect to `foodxchangepgfr.postgres.database.azure.com`

## Solution Steps

### Step 1: Configure Firewall in Azure Portal

1. Go to Azure Portal (https://portal.azure.com)
2. Navigate to: **foodxchange-rg** → **foodxchangepgfr** (PostgreSQL server)
3. In the left menu, click **Networking**
4. Under **Firewall rules**, add:
   - Rule name: `AllowMyIP`
   - Start IP: Your current IP (check at https://whatismyipaddress.com)
   - End IP: Same as Start IP
5. Also add:
   - Rule name: `AllowAzureServices`
   - Start IP: `0.0.0.0`
   - End IP: `0.0.0.0`
6. Click **Save**

### Step 2: Create Database User

Since you can't connect remotely yet, use Azure Portal's Query editor:

1. In your PostgreSQL server page, click **Query editor (preview)**
2. Login with your admin credentials
3. Run this SQL:

```sql
-- Create application user
CREATE USER foodxchange_app WITH PASSWORD 'Ud30078123';

-- Grant permissions
GRANT CONNECT ON DATABASE foodxchange_db TO foodxchange_app;
GRANT USAGE ON SCHEMA public TO foodxchange_app;
GRANT CREATE ON SCHEMA public TO foodxchange_app;
```

### Step 3: Test Connection

After firewall is configured, test with:

```bash
python test_azure_db.py
```

### Alternative: Use Admin Account First

If the user creation fails, first test with your admin account:

```python
# Modify test_azure_db.py to use admin credentials:
DATABASE_URL = "postgresql://YOUR_ADMIN_USER@foodxchangepgfr:YOUR_ADMIN_PASSWORD@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require"
```

Note: Azure PostgreSQL often requires the username format: `username@servername`

## Common Issues

1. **Firewall not configured**: Most common issue
2. **Wrong username format**: Try `foodxchange_app@foodxchangepgfr`
3. **SSL required**: Always use `sslmode=require`
4. **User doesn't exist**: Create user using Query editor in Azure Portal

## Next Steps

Once connected:
1. Run the full setup script to create all tables
2. Initialize Alembic for future migrations
3. Update App Service with connection string