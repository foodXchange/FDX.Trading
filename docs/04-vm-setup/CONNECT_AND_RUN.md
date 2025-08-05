# Quick Connect & Import Guide

## 1. Connect to VM (Any Method)

### Option A: Direct SSH
```bash
ssh azureuser@4.206.1.15
# Password: FDX2025!Import#VM
```

### Option B: Cursor
- Open Cursor
- Press F1 → "Remote-SSH: Connect to Host"
- Enter: azureuser@4.206.1.15
- Password: FDX2025!Import#VM

### Option C: PowerShell
```powershell
ssh azureuser@4.206.1.15
```

## 2. Run These Commands (Copy & Paste All)

```bash
# Setup environment (2 minutes)
sudo apt update && sudo apt install -y python3-pip
pip3 install pandas psycopg2-binary openpyxl python-dotenv

# Create project directory
mkdir -p ~/foodxchange && cd ~/foodxchange

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
EOF

# Download import script
wget https://raw.githubusercontent.com/your-repo/vm_fast_import.py -O import.py

# Or create it manually
nano import.py
# Then paste the vm_fast_import.py content
```

## 3. Upload Excel File

### From another terminal on your PC:
```bash
scp "C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/foodxchange/
# Enter password: FDX2025!Import#VM
```

## 4. Run Import!

```bash
# Back in VM terminal
cd ~/foodxchange
python3 import.py
```

## 5. Monitor Progress

The script will show:
- Current suppliers in database
- New suppliers to import
- Real-time progress with ETA
- Import rate (suppliers/minute)

## Expected Results:
- Total time: 15-30 minutes
- All 23,206 suppliers imported
- No timeout issues
- Ready for AI enhancement

## If Connection Fails:
1. Check VM is running:
```bash
az vm show --name fdx-founders-vm --resource-group foodxchange-founders-rg --query powerState
```

2. Try Azure Portal:
- Go to VM → Connect → Bastion or Cloud Shell