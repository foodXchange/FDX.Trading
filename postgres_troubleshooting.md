# PostgreSQL Connection Troubleshooting

## Current Status
- ✅ Server is reachable (ping succeeds)
- ❌ Port 5432 is blocked (TCP connection fails)
- Your actual IP: **85.65.236.169**

## Troubleshooting Steps

### 1. Verify Firewall Rules in Azure Portal

Go to your PostgreSQL server → Connection security and ensure:

1. **Your IP is correctly added**:
   - Rule name: `LocalDevelopment` 
   - Start IP: `85.65.236.169`
   - End IP: `85.65.236.169`

2. **Save was clicked** and shows "Update successful"

3. **Wait 2-3 minutes** for propagation

### 2. Check for Multiple Network Layers

Your connection might be blocked by:
- **Corporate firewall/proxy**
- **VPN** (disconnect VPN and try again)
- **ISP blocking port 5432**
- **Windows Firewall** (unlikely for outbound)

### 3. Alternative Connection Methods

#### Option A: Use Azure Cloud Shell
1. Open [Azure Cloud Shell](https://shell.azure.com)
2. Install psql: `sudo apt-get update && sudo apt-get install postgresql-client`
3. Connect: `psql "host=foodxchangepgfr.postgres.database.azure.com port=5432 dbname=foodxchange user=foodxchangedbadmin password=Ud30078123 sslmode=require"`

#### Option B: Use Azure Data Studio
1. Download [Azure Data Studio](https://docs.microsoft.com/en-us/sql/azure-data-studio/download)
2. Install PostgreSQL extension
3. Connect using your credentials

#### Option C: Use pgAdmin
1. Download [pgAdmin](https://www.pgadmin.org/download/)
2. Create new server connection:
   - Host: `foodxchangepgfr.postgres.database.azure.com`
   - Port: `5432`
   - Database: `foodxchange`
   - Username: `foodxchangedbadmin`
   - Password: `Ud30078123`
   - SSL mode: `Require`

### 4. Test from Different Network

Try connecting from:
- Mobile hotspot
- Different location
- Cloud VM (Azure VM in same region)

### 5. Verify Server Configuration

In Azure Portal, check:
- Server status: Should be "Ready"
- SSL enforcement: Should be "Enabled"
- Minimum TLS version: Try "TLS 1.0" temporarily

### 6. Connection String Variations

Try these formats:

```bash
# Format 1 - Standard
postgresql://foodxchangedbadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange?sslmode=require

# Format 2 - With escaped @
postgresql://foodxchangedbadmin%40foodxchangepgfr:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange?sslmode=require

# Format 3 - With SSL options
postgresql://foodxchangedbadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange?sslmode=require&sslcert=&sslkey=&sslrootcert=
```

## Quick Test Commands

### PowerShell Network Test:
```powershell
# Test DNS
nslookup foodxchangepgfr.postgres.database.azure.com

# Test port
Test-NetConnection -ComputerName foodxchangepgfr.postgres.database.azure.com -Port 5432

# Trace route
tracert foodxchangepgfr.postgres.database.azure.com
```

### Python Quick Test:
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex(('foodxchangepgfr.postgres.database.azure.com', 5432))
print(f"Port 5432 is {'open' if result == 0 else 'closed'}")
sock.close()
```

## If Nothing Works

1. **Create a support ticket** with Azure
2. **Use SQLite locally** for development
3. **Deploy directly to App Service** (bypass local connection)

The most common cause is the firewall rule not being properly saved or needing more time to propagate. Double-check the IP address in the Azure Portal matches exactly: **85.65.236.169**