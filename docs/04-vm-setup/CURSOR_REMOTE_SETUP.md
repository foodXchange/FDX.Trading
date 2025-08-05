# Cursor Remote SSH Setup - Step by Step

## Step 1: Install Cursor (2 minutes)
1. Download Cursor from: https://cursor.sh
2. Install on your Windows machine
3. Open Cursor

## Step 2: Install Remote-SSH Extension (1 minute)
1. In Cursor, press `Ctrl+Shift+X` (Extensions)
2. Search for "Remote - SSH"
3. Install the Microsoft "Remote - SSH" extension
4. Restart Cursor if prompted

## Step 3: Add SSH Key to Windows (2 minutes)

### If you have your SSH key:
```powershell
# In PowerShell, create SSH directory
mkdir ~\.ssh

# Copy your key file to SSH directory
# Replace path with your actual key location
copy "C:\path\to\your-key.pem" ~\.ssh\fdx-vm-key.pem

# Set correct permissions (Windows)
icacls ~\.ssh\fdx-vm-key.pem /inheritance:r /grant:r "%USERNAME%":"(R)"
```

### If you don't have the SSH key:
We'll use password authentication (see Step 4B)

## Step 4: Connect to VM

### Option A: With SSH Key
1. Press `F1` or `Ctrl+Shift+P`
2. Type "Remote-SSH: Connect to Host"
3. Enter: `azureuser@4.206.1.15`
4. Select your SSH config file (usually first option)
5. When prompted for key, browse to: `~\.ssh\fdx-vm-key.pem`

### Option B: With Password (if no key)
1. First, reset VM password in Azure Portal:
   - Go to your VM in Azure Portal
   - Click "Reset password" under Support
   - Set new password
2. Connect same as above, enter password when prompted

## Step 5: First Time Setup (5 minutes)
Once connected, Cursor will install VS Code Server on VM automatically.

Open a new terminal in Cursor (`Ctrl+``), you're now on the VM!

## Step 6: Quick Project Setup
```bash
# You're now in VM terminal!
# Install Python packages
sudo apt update
sudo apt install -y python3-pip
pip3 install pandas psycopg2-binary openpyxl python-dotenv openai==0.28

# Create project directory
mkdir ~/foodxchange
cd ~/foodxchange

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
EOF

echo "✅ Environment ready!"
```

## Step 7: Upload Files to VM

### Option 1: Drag & Drop in Cursor
1. In Cursor's Explorer panel (left side)
2. Simply drag your Excel file from Windows Explorer
3. Drop it into the `~/foodxchange` folder

### Option 2: Use Terminal
```bash
# From your Windows machine (Git Bash or PowerShell)
scp "C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/foodxchange/
```

## Step 8: Create Import Script
In Cursor, create new file `import_suppliers.py`:

```python
#!/usr/bin/env python3
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("Starting FoodXchange import...")
print("Connecting to Azure PostgreSQL...")

# Your import code here
# I'll help you write it once connected!
```

## Troubleshooting

### Can't find SSH key?
- Check Azure Portal → VM → "Connect" → "Download RDP file" section
- Or reset password and use password auth

### Connection refused?
- Make sure VM is running:
```bash
az vm start --name fdx-founders-vm --resource-group foodxchange-founders-rg
```

### Permission denied?
- Check key permissions
- Try password authentication

## You're Ready! 🚀
Once connected, you'll have:
- Cursor IDE with Claude/GPT-4
- Terminal running ON the Azure VM
- Direct, fast database access
- No timeout issues!

Let me know when you're connected and I'll help with the import!