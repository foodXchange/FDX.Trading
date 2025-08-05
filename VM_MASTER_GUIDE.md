# FDX VM Master Guide
*Last Updated: August 5, 2025*

## VM Overview

- **IP Address**: 4.206.1.15
- **Hostname**: fdx-founders-vm
- **OS**: Ubuntu 22.04.5 LTS
- **User**: fdxfounder (only user)
- **SSH Key**: `~/.ssh/fdx_founders_key`

## Quick Access

### SSH Connection
```bash
# General access
ssh fdx-vm

# Development with port forwarding
ssh fdx-dev
```

### Web Access
- **Main App**: http://4.206.1.15 (port 80)
- **Database**: Azure PostgreSQL (23,206+ suppliers)

## SSH Configuration

Your `~/.ssh/config` contains:
```
# FoodXchange VM - Main connection
Host fdx-vm
    HostName 4.206.1.15
    User fdxfounder
    Port 22
    IdentityFile ~/.ssh/fdx_founders_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ForwardAgent yes

# FoodXchange VM - Development with port forwarding
Host fdx-dev
    HostName 4.206.1.15
    User fdxfounder
    Port 22
    IdentityFile ~/.ssh/fdx_founders_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ForwardAgent yes
    LocalForward 8000 localhost:80
    LocalForward 8003 localhost:8003
    LocalForward 3000 localhost:3000
    LocalForward 19999 localhost:19999
```

## Directory Structure

```
/home/fdxfounder/
├── fdx/
│   ├── app/           # Main FDX application
│   ├── backups/       # Backup files
│   ├── data/          # Data files
│   ├── logs/          # Application logs
│   ├── monitoring/    # Monitoring scripts
│   ├── scripts/       # Utility scripts
│   └── secrets/       # Sensitive configurations
├── FDX-Crawler/       # Web crawler application
└── Workspace1/        # Additional workspace
```

## Essential Commands

### Connect to VM
```bash
# Simple connection
ssh fdx-vm

# Go directly to app directory
ssh fdx-vm "cd /home/fdxfounder/fdx/app && bash"
```

### Check Application Status
```bash
# View app status
ssh fdx-vm "sudo systemctl status foodxchange"

# Restart app
ssh fdx-vm "sudo systemctl restart foodxchange"

# View logs
ssh fdx-vm "tail -f /home/fdxfounder/fdx/app/logs/app.log"
```

### Database Operations
```bash
# Check supplier count
ssh fdx-vm "cd /home/fdxfounder/fdx/app && python3 -c 'from database import get_db_connection; conn = get_db_connection(); cur = conn.cursor(); cur.execute(\"SELECT COUNT(*) FROM suppliers\"); print(f\"Suppliers: {cur.fetchone()[0]:,}\")'"

# Database connection string (in .env)
# postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
```

### File Transfer
```bash
# Upload file to VM
scp local_file.txt fdx-vm:/home/fdxfounder/

# Download from VM
scp fdx-vm:/home/fdxfounder/file.txt ./

# Sync directory to VM
rsync -avz --exclude='.git' ./ fdx-vm:/home/fdxfounder/fdx/app/
```

## Development Workflow

### Option 1: VS Code Remote SSH
```bash
# Command line
code --remote ssh-remote+fdx-vm /home/fdxfounder/fdx/app

# Or use VS Code UI:
# 1. Ctrl+Shift+P
# 2. "Remote-SSH: Connect to Host"
# 3. Select "fdx-vm"
```

### Option 2: Direct SSH Development
```bash
# Connect
ssh fdx-vm

# Navigate to app
cd /home/fdxfounder/fdx/app

# Edit files
nano app.py

# Run development server
python3 app.py
```

### Option 3: Claude Code + SSH
```bash
# Use claude_vm_connect.bat for guided connection
C:\Users\foodz\Desktop\FoodXchange\claude_vm_connect.bat
```

## Quick Scripts

### Upload Excel to VM
```bash
# Use the helper script
C:\Users\foodz\Desktop\FoodXchange\upload_excel_to_vm.bat
```

### Open Dashboards
```bash
# Use the dashboard launcher
C:\Users\foodz\Desktop\FoodXchange\Open_Dashboards.bat
```

## Service Management

### Main Application
- **Service**: foodxchange.service
- **Port**: 80
- **Process**: Python/Gunicorn

### Commands
```bash
# Start/Stop/Restart
sudo systemctl start foodxchange
sudo systemctl stop foodxchange
sudo systemctl restart foodxchange

# Enable/Disable autostart
sudo systemctl enable foodxchange
sudo systemctl disable foodxchange

# View service logs
sudo journalctl -u foodxchange -f
```

## Security Notes

1. **Single User**: Only `fdxfounder` user exists (azureuser removed)
2. **SSH Key**: Private key at `~/.ssh/fdx_founders_key`
3. **Firewall**: Ports 80, 22 open
4. **Database**: Hosted on Azure PostgreSQL (not on VM)

## Troubleshooting

### SSH Connection Issues
```bash
# Test connection
ssh -v fdx-vm

# Clear known hosts if needed
ssh-keygen -R 4.206.1.15
```

### Application Not Responding
```bash
# Check if running
ssh fdx-vm "sudo systemctl status foodxchange"

# Check ports
ssh fdx-vm "sudo ss -tlnp | grep :80"

# Restart service
ssh fdx-vm "sudo systemctl restart foodxchange"
```

### Database Connection
```bash
# Test from VM
ssh fdx-vm "cd /home/fdxfounder/fdx/app && python3 -c 'from database import get_db_connection; conn = get_db_connection(); print(\"Connected!\" if conn else \"Failed!\")'"
```

## Important Paths

- **App Code**: `/home/fdxfounder/fdx/app/`
- **Environment**: `/home/fdxfounder/fdx/app/.env`
- **Logs**: `/home/fdxfounder/fdx/app/logs/`
- **Python**: `/usr/bin/python3`
- **Service File**: `/etc/systemd/system/foodxchange.service`

## Next Steps

1. For development, use VS Code with Remote SSH
2. For quick edits, use direct SSH
3. For automation, use the provided .bat scripts
4. Always check logs if issues arise

---

*This is the master VM documentation. All other VM docs have been consolidated here.*