# pgAdmin Setup Guide for Azure PostgreSQL

## Step 1: Download and Install pgAdmin
1. Go to https://www.pgadmin.org/download/
2. Download pgAdmin 4 for Windows
3. Run the installer and follow the setup wizard

## Step 2: Connect to Your Azure PostgreSQL Database

### Connection Details (from your Azure setup):
- **Host**: `foodxchangepgfr.postgres.database.azure.com`
- **Port**: 5432
- **Database**: `foodxchange_db`
- **Username**: `pgadmin`
- **Password**: `Ud30078123`

### Steps in pgAdmin:
1. Open pgAdmin
2. Right-click on "Servers" → "Register" → "Server"
3. In the "General" tab:
   - Name: `FoodXchange Azure DB`
4. In the "Connection" tab:
   - Host: `foodxchangepgfr.postgres.database.azure.com`
   - Port: 5432
   - Database: `foodxchange_db`
   - Username: `pgadmin`
   - Password: `Ud30078123`
5. Click "Save"

## Step 3: Basic Operations

### View Tables:
- Expand your server → Databases → foodxchange_db → Schemas → public → Tables
- Right-click any table → "View/Edit Data" → "All Rows"

### Run Queries:
- Click the SQL button (magnifying glass icon) or Tools → Query Tool
- Type: `SELECT * FROM users LIMIT 10;`
- Click the Execute button (play button)

### Common Commands:
```sql
-- View all tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- View table structure
\d table_name

-- Count records in a table
SELECT COUNT(*) FROM users;
```

## Troubleshooting:
- If connection fails, check your Azure firewall settings
- Make sure your IP is whitelisted in Azure PostgreSQL firewall rules
- Verify the server name and credentials are correct 