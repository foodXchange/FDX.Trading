# Cursor IDE Remote SSH Setup - Poland VM

## 🚀 Quick Setup in Cursor

### 1. Open Cursor IDE

### 2. Connect to Remote SSH:
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type: "Remote-SSH: Connect to Host"
- Select: **`fdx-poland`** (new Poland VM)
  - Or use **`fdx`** for short
  - Or use **`fdx-poland-dev`** for port forwarding

### 3. First Time Connection:
- Select Linux as the platform
- Continue if prompted about fingerprint
- Wait for VS Code Server to install

### 4. Open Project Folder:
- Once connected, click "Open Folder"
- Navigate to: `/home/fdxadmin/fdx`
- This is your application directory

## 📁 SSH Config Hosts

### New Poland VM (Use These):
- **`fdx-poland`** - Main connection (74.248.141.31)
- **`fdx-poland-dev`** - With port forwarding
- **`fdx`** - Quick shorthand

### Old US VM (Being Deleted):
- ~~`fdx-vm`~~ - DEPRECATED
- ~~`fdx-dev`~~ - DEPRECATED

## 🔌 Port Forwarding (fdx-poland-dev)

When using `fdx-poland-dev`, these ports are forwarded:
- **8000** → localhost:8000 (Application)
- **8080** → localhost:80 (Nginx)
- **3000** → localhost:3000 (Grafana)
- **19999** → localhost:19999 (Netdata)

## 🛠️ Terminal Commands in Cursor

Once connected, you can run:
```bash
# Check application
cd /home/fdxadmin/fdx
ls -la

# View logs
sudo journalctl -u fdx -f

# Restart services
sudo systemctl restart fdx
sudo systemctl restart nginx

# Check Python environment
source venv/bin/activate
python --version
```

## ⚡ Benefits of Poland VM

- **6x faster** from Israel (30ms vs 200ms)
- **Cheaper** ($57 vs $60/month)
- **Better organized** resource groups

## 🗑️ Remove Old Connections

In Cursor, you can clean up old connections:
1. Press `Ctrl+Shift+P`
2. Type: "Remote-SSH: Open Configuration File"
3. Old connections are commented out (lines starting with #)
4. You can delete the commented lines if desired

## 📝 Notes

- Username: `fdxadmin` (not fdxfounder)
- IP: `74.248.141.31` (Poland)
- Key: `~/.ssh/id_rsa` (auto-generated)