# Azure PostgreSQL Setup Guide for FoodXchange

## Prerequisites
- Azure PostgreSQL Flexible Server: `foodxchangepgfr`
- Resource Group: `foodxchange-rg`
- Database: `foodxchange_db` (already created)
- Admin access to the PostgreSQL server

## Step 1: Create App User and Set Permissions

### Option A: Using pgAdmin
1. Connect to your Azure PostgreSQL server using pgAdmin:
   - Server: `foodxchangepgfr.postgres.database.azure.com`
   - Port: `5432`
   - Database: `foodxchange_db`
   - Username: Your admin username
   - Password: Your admin password

2. Open Query Tool and run the setup script (`database/setup_azure_db.sql`)

3. **IMPORTANT**: Replace `YOUR_SECURE_PASSWORD_HERE` with a strong password

### Option B: Using Azure Cloud Shell
```bash
# Connect to the database
psql "host=foodxchangepgfr.postgres.database.azure.com port=5432 dbname=foodxchange_db user=YOUR_ADMIN_USER sslmode=require"

# Run the setup script
\i setup_azure_db.sql
```

## Step 2: Configure App Service Environment Variables

In your Azure App Service, set these environment variables:

```bash
DATABASE_URL=postgresql://foodxchange_app:YOUR_APP_PASSWORD@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require

# Optional: Individual components (if not using DATABASE_URL)
DB_HOST=foodxchangepgfr.postgres.database.azure.com
DB_PORT=5432
DB_NAME=foodxchange_db
DB_USER=foodxchange_app
DB_PASSWORD=YOUR_APP_PASSWORD
```

## Step 3: Configure SSL/TLS (Required for Azure)

Azure PostgreSQL requires SSL connections. The connection string above includes `sslmode=require`.

For local development/testing:
```python
# .env file
DATABASE_URL=postgresql://foodxchange_app:YOUR_APP_PASSWORD@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require
```

## Step 4: Test the Connection

Run this test script locally:

```python
import os
import psycopg2
from sqlalchemy import create_engine

# Test with psycopg2
conn_string = "host='foodxchangepgfr.postgres.database.azure.com' dbname='foodxchange_db' user='foodxchange_app' password='YOUR_APP_PASSWORD' sslmode='require'"
try:
    conn = psycopg2.connect(conn_string)
    print("psycopg2 connection successful!")
    conn.close()
except Exception as e:
    print(f"psycopg2 connection failed: {e}")

# Test with SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL")
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("SQLAlchemy connection successful!")
except Exception as e:
    print(f"SQLAlchemy connection failed: {e}")
```

## Step 5: Initialize the Database

Once connected, the application will automatically create tables using SQLAlchemy migrations. You can also manually run:

```bash
# From the FoodXchange directory
python scripts/init_db.py
```

## Security Best Practices

1. **Password Management**:
   - Use Azure Key Vault for storing database passwords
   - Never commit passwords to source control
   - Use managed identities where possible

2. **Network Security**:
   - Enable firewall rules for your App Service
   - Use private endpoints for production
   - Restrict access to specific IP ranges

3. **Least Privilege**:
   - The `foodxchange_app` user has only the necessary permissions
   - No CREATE/DROP database permissions
   - Limited to CRUD operations on application tables

## Troubleshooting

### Connection Issues
1. Check firewall rules allow your IP
2. Verify SSL is enabled in connection string
3. Ensure username format is correct (not email format)

### Permission Issues
1. Verify the app user was created successfully
2. Check grants were applied to all tables
3. Ensure schema permissions are correct

### SSL Certificate Issues
If you get SSL certificate errors:
1. Download Azure's SSL certificate
2. Add to connection string: `sslmode=require&sslcert=path/to/cert`

## Monitoring

Set up these Azure Monitor alerts:
- Database connection failures
- High query execution time
- Storage usage > 80%
- CPU usage > 80%

## Backup Strategy

Azure PostgreSQL Flexible Server includes:
- Automated backups (7-35 days retention)
- Point-in-time restore
- Geo-redundant backups (optional)

Configure backup retention in Azure Portal under:
`Server > Settings > Backup & Restore`