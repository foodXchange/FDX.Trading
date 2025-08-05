# Cursor IDE - Remote SSH Setup for FDX VM

## Quick Setup (Uses System SSH Config)

Since you already have SSH configured in `~/.ssh/config`, Cursor will use it automatically.

### Steps to Connect:

1. **Open Cursor**

2. **Open Command Palette**
   - Press `Ctrl+Shift+P` (Windows)

3. **Connect to VM**
   - Type: `Remote-SSH: Connect to Host...`
   - Select: `fdx-vm` (from your SSH config)

4. **Open Folder**
   - Once connected, open folder: `/home/fdxfounder/fdx/app`

### Alternative: Direct Connection Command

In Cursor's terminal:
```bash
# This will open Cursor connected to the VM
cursor --remote ssh-remote+fdx-vm /home/fdxfounder/fdx/app
```

## Your SSH Hosts in Cursor

These hosts are available from your `~/.ssh/config`:

- **fdx-vm** - General VM access
- **fdx-dev** - VM with port forwarding (8000, 8003, 3000, 19999)

## Troubleshooting

### If "Remote-SSH" is not available:
1. Press `Ctrl+Shift+X` (Extensions)
2. Search: "Remote - SSH"
3. Install the official Microsoft extension
4. Restart Cursor

### If connection fails:
1. Test SSH in terminal first: `ssh fdx-vm`
2. Ensure your SSH key has correct permissions
3. Check Windows SSH Agent is running

## Quick Commands in Cursor

Once connected, use Cursor's integrated terminal:

```bash
# You're already in the VM as fdxfounder!

# Go to app directory
cd /home/fdxfounder/fdx/app

# Check database
python3 -c "from database import get_db_connection; conn = get_db_connection(); print('DB Connected!' if conn else 'DB Error')"

# View logs
tail -f logs/app.log

# Restart service
sudo systemctl restart foodxchange
```

## Port Forwarding

If you connected with `fdx-dev`, these ports are forwarded:
- http://localhost:8000 → VM port 80 (main app)
- http://localhost:8003 → VM port 8003
- http://localhost:3000 → VM port 3000
- http://localhost:19999 → VM port 19999

---

*Your VM is ready for development with Cursor!*