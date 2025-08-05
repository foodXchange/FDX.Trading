# Upload All 23,206 Suppliers via Azure VM

## Quick Steps:

### 1. Connect to Your VM
```bash
ssh -i <your-ssh-key> azureuser@4.206.1.15
```

### 2. Quick Setup (if not done already)
```bash
# Install Python packages
sudo apt update
sudo apt install -y python3-pip postgresql-client
pip3 install pandas psycopg2-binary openpyxl python-dotenv openai==0.28
```

### 3. Upload Files (from your Windows machine)

#### Option A: Using SCP (Git Bash)
```bash
# Upload Excel file
scp -i <key> "C:/Users/foodz/Downloads/Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/

# Upload .env file
scp -i <key> .env azureuser@4.206.1.15:~/

# Upload import script
scp -i <key> vm_import.py azureuser@4.206.1.15:~/
```

#### Option B: Using Azure CLI
```bash
# Upload to VM using Azure CLI
az vm run-command invoke \
  --resource-group foodxchange-founders-rg \
  --name fdx-founders-vm \
  --command-id RunShellScript \
  --scripts "wget https://your-file-url/suppliers.xlsx"
```

### 4. Run Import on VM
```bash
# Start a screen session (so it keeps running)
screen -S import

# Run the import
python3 vm_import.py

# Detach screen (Ctrl+A, then D)
# Check progress later: screen -r import
```

### 5. Monitor Progress
```bash
# Check log
tail -f vm_import.log

# Check database directly
psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" \
  -c "SELECT COUNT(*) FROM suppliers;"
```

## Expected Timeline:
- Setup: 5 minutes
- File upload: 2-3 minutes
- Import all 23,206 suppliers: 30-60 minutes
- With AI enhancement: 2-3 hours

## If SSH Key is Missing:
Use password authentication or Azure Portal:
1. Go to Azure Portal → Your VM
2. Click "Connect" → "Connect via Bastion" or "Reset password"