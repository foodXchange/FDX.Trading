# Easy Way to Upload All Suppliers

## Option 1: Use Azure Portal Console (Easiest)

1. Go to [Azure Portal](https://portal.azure.com)
2. Find your VM: **fdx-founders-vm**
3. Click **Connect** → **Connect via Bastion** or **Cloud Shell**
4. Upload files directly through the browser

## Option 2: Create Storage Account & Upload

### Step 1: Create Storage (2 minutes)
```bash
az storage account create \
  --name fdxstorage2025 \
  --resource-group fdx-trading-rg \
  --location canadacentral \
  --sku Standard_LRS
```

### Step 2: Upload Excel File
```bash
# Get storage key
$key = az storage account keys list --account-name fdxstorage2025 --query "[0].value" -o tsv

# Create container
az storage container create --name imports --account-name fdxstorage2025 --account-key $key

# Upload file
az storage blob upload \
  --account-name fdxstorage2025 \
  --account-key $key \
  --container-name imports \
  --name suppliers.xlsx \
  --file "C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx"
```

### Step 3: Download on VM
```bash
# On the VM
wget https://fdxstorage2025.blob.core.windows.net/imports/suppliers.xlsx
```

## Option 3: Direct Database Import (From Your PC)

Since VM connection is complex, let's try a different approach:

1. **Upgrade PostgreSQL to General Purpose** (better performance):
```bash
az postgres flexible-server update \
  --name fdx-postgres-server \
  --resource-group fdx-trading-rg \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose
```

2. **Add your IP to firewall**:
```bash
# Get your IP
curl ifconfig.me

# Add firewall rule
az postgres flexible-server firewall-rule create \
  --name home-ip \
  --resource-group fdx-trading-rg \
  --server-name fdx-postgres-server \
  --start-ip-address YOUR-IP \
  --end-ip-address YOUR-IP
```

3. **Run import locally** with the simple script I created

## Which option would you prefer?
1. Azure Portal (easiest, no SSH needed)
2. Storage Account (good for large files)
3. Direct import (if we can fix the connection)