# 🔧 Cursor PostgreSQL Setup - Troubleshooting Guide

## Common Errors and Solutions

### Error: "Can't find" or "Connection failed"

## Step 1: Install Extensions First
1. Open Cursor
2. Press `Ctrl+Shift+X`
3. Search for **"SQLTools"**
4. Click Install on "SQLTools - Database tools" by Matheus Teixeira
5. Also install **"SQLTools PostgreSQL/Cockroach Driver"**

## Step 2: Alternative Connection Method

### Method A: Using Connection String
1. Press `F1` in Cursor
2. Type: `SQLTools: Add New Connection`
3. Choose **"PostgreSQL"**
4. Select **"CONNECTION STRING"** mode
5. Paste this:
```
postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
```
6. Name it: `FoodXchange Azure`
7. Test Connection

### Method B: Manual Setup
1. Press `F1`
2. Type: `SQLTools: Add New Connection`
3. Choose **"PostgreSQL"**
4. Fill in:
   - Connection name: `FoodXchange Azure`
   - Server: `fdx-postgres-server.postgres.database.azure.com`
   - Port: `5432`
   - Database: `foodxchange`
   - Username: `fdxadmin`
   - Password: `FDX2030!`
   - SSL: `Require`

## Step 3: If Still Not Working

### Check 1: Test Connection from Command Line
```cmd
psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" -c "SELECT 1"
```

### Check 2: Install PostgreSQL Client
- Download from: https://www.postgresql.org/download/windows/
- Install "Command Line Tools" only

### Check 3: Firewall
- Windows Defender might block connection
- Add Cursor to firewall exceptions

## Step 4: Alternative - Use Database Client Extension
1. Install **"Database Client"** by Weijan Chen
2. Click database icon in sidebar
3. Click **"+"** → **"PostgreSQL"**
4. Use the connection details above

## Quick Test Query
Once connected, create a new file `test.sql`:
```sql
SELECT COUNT(*) FROM suppliers;
```
Select the text and press `Ctrl+E` to execute.

## Still Having Issues?
Try the web-based Azure Query Editor:
https://portal.azure.com → Your PostgreSQL server → Query editor (preview)