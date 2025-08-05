# 🚀 FoodXchange Azure VM Documentation

## 📋 VM Connection Details

**Your VM is now live and running!**

- **Public IP**: `4.206.1.15`
- **Username**: `fdxfounder`
- **SSH Key**: `~/.ssh/fdx_founders_key`
- **Location**: East US
- **VM Size**: B4ms (4 vCPU, 16GB RAM)
- **Monthly Cost**: FREE (using Founders Hub $150/month credits)

## 🔐 How to Connect

### From Windows (Git Bash/WSL)
```bash
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
```

### From iPhone/iPad (Using Termius)
1. Download Termius from App Store
2. Create new host:
   - Hostname: `4.206.1.15`
   - Username: `fdxfounder`
   - Port: `22`
3. Import SSH key:
   - Copy contents of `~/.ssh/fdx_founders_key`
   - Paste into Termius key management

### From Mac/Linux
```bash
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
```

## 📱 Persistent Claude Sessions

### Start Claude Session (First Time)
```bash
# Connect to VM
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15

# Start all sessions
fdx-start

# Attach to Claude development
fdx-claude
```

### Daily Workflow
```bash
# Morning: Connect and attach
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
fdx-claude  # Attaches to existing session

# Work with Claude...

# Evening: Detach (keeps running!)
Ctrl+B then D
```

## 🛠️ Essential Commands

### Session Management
| Command | Description |
|---------|-------------|
| `fdx-start` | Start all tmux sessions |
| `fdx-claude` | Attach to Claude development session |
| `fdx-prod` | Attach to production monitoring |
| `fdx-status` | Check all running sessions |
| `fdx-stop` | Stop all sessions |

### Quick Navigation
| Command | Description |
|---------|-------------|
| `fdx` | Go to app directory |
| `activate` | Activate Python environment |
| `fdx-logs` | View application logs |
| `fdx-backup` | Run manual backup |

### Service Control
| Command | Description |
|---------|-------------|
| `sudo systemctl status fdx-app` | Check app status |
| `sudo systemctl restart fdx-app` | Restart app |
| `sudo systemctl status nginx` | Check nginx status |
| `fdx-health` | Run health check |

## 🌐 Web Services

Access these from any browser:

- **FastAPI App**: http://4.206.1.15
- **Grafana Monitoring**: http://4.206.1.15:3000 (admin/admin)
- **Netdata Real-time**: http://4.206.1.15:19999

## 💾 Database Connection

Your PostgreSQL database is running but needs the connection URL:

```bash
# SSH to VM first
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15

# Edit environment file
cd ~/fdx/app
nano .env

# Add your existing database URL:
DATABASE_URL=postgresql://fdxadmin:FDX2030!@foodxchange-flex-db.postgres.database.azure.com:5432/foodxchange?sslmode=require
```

## 📱 Mobile-Friendly tmux Controls

When connected via iPhone/Termius:

| Action | Command |
|--------|---------|
| Detach session | `Ctrl+B` then `D` |
| Switch windows | `Ctrl+B` then window number |
| Scroll up/down | `Ctrl+B` then `[` (then use arrows) |
| Exit scroll mode | `q` |
| Create new window | `Ctrl+B` then `C` |
| Kill current pane | `Ctrl+B` then `X` |

## 💰 Cost Management

### Current Usage (FREE with Founders Hub)
- VM (B4ms): $0 (normally $120/month)
- Storage: $0 (normally $20/month)
- Total: $0/month for 2 years!

### Monitor Credit Usage
```bash
# From your local machine
./monitor_founders_credits.sh
```

### Stop VM to Save Credits
```bash
# Deallocate when not using
az vm deallocate --resource-group foodxchange-founders-rg --name fdx-founders-vm

# Start when needed
az vm start --resource-group foodxchange-founders-rg --name fdx-founders-vm
```

## 🔧 Configuration Tasks

### 1. Update Environment Variables
```bash
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
cd ~/fdx/app
cp .env.template .env
nano .env

# Add your keys:
# - DATABASE_URL (your existing PostgreSQL)
# - ANTHROPIC_API_KEY
# - AZURE_OPENAI_KEY (already in your local .env)
# - SENDGRID_API_KEY (when ready)
```

### 2. Install Your App Dependencies
```bash
cd ~/fdx/app
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Your FastAPI App
```bash
# Development mode
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or production mode
gunicorn -c gunicorn_config.py app:app
```

## 🚨 Troubleshooting

### Can't Connect via SSH
```bash
# Check VM status
az vm get-instance-view \
  --resource-group foodxchange-founders-rg \
  --name fdx-founders-vm \
  --query instanceView.statuses[1]

# Check firewall rules
az network nsg rule list \
  --resource-group foodxchange-founders-rg \
  --nsg-name fdx-founders-vm-nsg \
  --output table
```

### tmux Session Issues
```bash
# List all sessions
tmux ls

# Kill stuck session
tmux kill-session -t session-name

# Start fresh
fdx-start
```

### Service Not Starting
```bash
# Check logs
sudo journalctl -u fdx-app -f

# Check Python errors
cd ~/fdx/app
source venv/bin/activate
python -m app  # See direct errors
```

## 📝 Quick Reference Card

Save this for easy access:

```
==========================================
FOODXCHANGE VM QUICK REFERENCE
==========================================
IP: 4.206.1.15
SSH: ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15

DAILY COMMANDS:
fdx-start     - Start everything
fdx-claude    - Open Claude
fdx-status    - Check status
Ctrl+B, D     - Detach (keep running)

URLS:
App:     http://4.206.1.15
Grafana: http://4.206.1.15:3000
Netdata: http://4.206.1.15:19999

HELP:
fdx-logs      - View logs
fdx-health    - Health check
usage         - System stats
==========================================
```

## 🎯 Next Steps

1. **Copy your .env settings**:
   ```bash
   # From local machine
   scp -i ~/.ssh/fdx_founders_key .env fdxfounder@4.206.1.15:~/fdx/app/.env
   ```

2. **Test the connection**:
   ```bash
   ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
   fdx-status
   ```

3. **Start Claude session**:
   ```bash
   fdx-start
   fdx-claude
   ```

4. **Configure domain** (optional):
   - Point your domain to 4.206.1.15
   - Run: `sudo certbot --nginx -d yourdomain.com`

---

**Need help?** Your VM is fully configured and ready. The Claude sessions will persist even when you disconnect!