# Import Strategy Using Azure VM

Since you have an Azure VM (fdx-founders-vm) with better connectivity to Azure services, here's the strategy:

## Option 1: Direct Import from VM

1. SSH into your VM:
```bash
ssh -i <your-key> azureuser@<vm-public-ip>
```

2. Install required tools on VM:
```bash
sudo apt update
sudo apt install python3-pip postgresql-client
pip3 install pandas psycopg2-binary openpyxl python-dotenv
```

3. Upload the Excel file to VM:
```bash
scp -i <your-key> "C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx" azureuser@<vm-ip>:~/
```

4. Run import from VM for better connectivity

## Option 2: Use Azure Storage

1. Upload Excel to Azure Blob Storage
2. Access from VM or any Azure service
3. Import with better network performance

## Option 3: Upgrade PostgreSQL Tier

With your Founders Hub benefits, consider upgrading to:
- **General Purpose tier** for better performance
- **More vCores** for concurrent connections
- **Connection pooling** with PgBouncer

## Current Status
- Database: fdx-postgres-server (Burstable B1ms)
- Location: Israel Central
- Current suppliers: ~6,000+
- Target: 23,206 suppliers

The connection timeouts suggest network latency or tier limitations. Using the Azure VM will provide:
- Better network connectivity (same Azure backbone)
- Lower latency
- More stable connections
- Ability to run long imports without local timeouts