# UPDATE VM WITH NEW DATABASE CONNECTION

## Manual Steps to Update Your VM:

### 1. Connect to your VM:
```bash
ssh azureuser@4.206.1.15
# Enter your password when prompted
```

### 2. Once connected, run these commands:

```bash
# Go to your app directory
cd ~/fdx

# Backup current .env
cp .env .env.backup

# Update the DATABASE_URL
nano .env
```

### 3. In the nano editor:
- Find the line starting with `DATABASE_URL=`
- Delete the old line
- Add this new line:
```
DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require
```
- Press `Ctrl+X`, then `Y`, then `Enter` to save

### 4. Test the new connection:
```bash
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM suppliers')
print(f'Connected! Suppliers: {cur.fetchone()[0]}')
"
```

### 5. Restart your application:
```bash
# Kill existing process
pkill -f uvicorn

# Start with new database
nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

### 6. Verify it's working:
```bash
# Check if running
ps aux | grep uvicorn

# Check logs
tail -f app.log
```

## Important Notes:

⚠️ **Current Status:**
- **New Database**: Only has 3,000 suppliers (partial data)
- **Old Database**: Has all 16,963 suppliers (but orphaned)

## To Complete Migration (after updating VM):

Run this on the VM to import remaining data:
```bash
# Option 1: Import from Excel files (if available on VM)
python3 import_suppliers_excel.py

# Option 2: Copy from old database (if still accessible)
python3 migrate_remaining_suppliers.py
```

## New Connection Details:
- **Server**: fdx-postgres-production.postgres.database.azure.com
- **Database**: foodxchange
- **Username**: fdxadmin
- **Password**: FoodXchange2024
- **Resource Group**: fdx-production-rg
- **Location**: Canada Central

Your website will work with the new database, but with only 3,000 suppliers until you complete the data migration.