# Azure VM Import Instructions

## Your VM Details
- **VM Name:** fdx-founders-vm
- **Public IP:** 4.206.1.15
- **Username:** azureuser
- **OS:** Ubuntu 22.04 LTS

## Step 1: Connect to VM
```bash
ssh -i <your-ssh-key> azureuser@4.206.1.15
```

## Step 2: Run Setup (on VM)
```bash
# Make setup script executable
chmod +x vm_setup.sh

# Run the setup
./vm_setup.sh
```

## Step 3: Upload Files
From your Windows machine, use one of these methods:

### Option A: Using SCP (Git Bash)
```bash
# Upload Excel file
scp -i <key> "C:/Users/foodz/Downloads/Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/

# Upload .env file
scp -i <key> .env azureuser@4.206.1.15:~/

# Upload import script
scp -i <key> vm_import.py azureuser@4.206.1.15:~/
```

### Option B: Using WinSCP
1. Download WinSCP
2. Connect with your SSH key
3. Drag and drop files

## Step 4: Run Import (on VM)
```bash
# Activate Python environment
source ~/foodxchange/venv/bin/activate

# Run the import
python3 vm_import.py
```

## Running in Background
To keep import running after disconnect:
```bash
# Using screen
screen -S import
python3 vm_import.py
# Press Ctrl+A then D to detach

# Check progress later
screen -r import
```

## Monitor Progress
```bash
# Check log file
tail -f vm_import.log

# Check database count
psql -h fdx-postgres-server.postgres.database.azure.com -U fdxadmin -d foodxchange -c "SELECT COUNT(*) FROM suppliers;"
```

## Benefits of VM Import:
- ✅ Same Azure network = 10x faster
- ✅ No timeout issues
- ✅ Can run 24/7
- ✅ Better connection stability
- ✅ Included in your Founders Hub benefits

The import will complete all 23,206 suppliers with AI enhancement!