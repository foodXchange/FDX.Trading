# Keep Claude & Import Running - Quick Guide

## 🚀 One-Time Setup (5 minutes)

### 1. Connect to VM
```bash
ssh azureuser@4.206.1.15
# Password: FDX2025!Import#VM
```

### 2. Run Setup Script
```bash
# Download and run the setup script
curl -O https://raw.githubusercontent.com/foodxchange/setup/main/tmux_persistent_setup.sh
bash tmux_persistent_setup.sh
```

OR manually:

```bash
# Quick setup commands
sudo apt update && sudo apt install -y tmux python3-pip
pip3 install pandas psycopg2-binary openpyxl python-dotenv openai==0.28
mkdir -p ~/foodxchange && cd ~/foodxchange

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
EOF
```

### 3. Upload Files (from your PC)
```bash
# Open new terminal on your PC
scp "C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/foodxchange/
scp ai_enhanced_import.py azureuser@4.206.1.15:~/foodxchange/
```

## 🔄 Start Persistent Import

### Create tmux sessions:
```bash
# Import session (runs the actual import)
tmux new -s import -d
tmux send-keys -t import "cd ~/foodxchange && python3 ai_enhanced_import.py" C-m

# Monitor session (shows progress every minute)
tmux new -s monitor -d
tmux send-keys -t monitor "watch -n 60 'python3 ~/foodxchange/check_progress.py'" C-m

# Logs session (shows real-time logs)
tmux new -s logs -d
tmux send-keys -t logs "tail -f ~/foodxchange/ai_import.log" C-m
```

## 📱 Check Progress (from anywhere)

### From iPhone/Computer:
```bash
ssh azureuser@4.206.1.15

# Quick status
~/foodxchange/status.sh

# View import progress
tmux attach -t import
# Press Ctrl+B then D to detach

# View monitor
tmux attach -t monitor
# Press Ctrl+B then D to detach
```

## 🎯 What Happens:

1. **Import keeps running** - Even if you disconnect
2. **Auto-progress tracking** - Monitor updates every minute
3. **Complete safety** - tmux preserves sessions through disconnections
4. **23,206 suppliers** - All will be imported with AI enhancement
5. **2-3 hours total** - Runs at ~150-200 suppliers/minute

## 🆘 Troubleshooting

### If import stops:
```bash
tmux attach -t import
# Press Ctrl+C to stop
python3 ai_enhanced_import.py  # Restart
```

### Check what's running:
```bash
tmux ls  # List all sessions
ps aux | grep python  # See Python processes
```

### Emergency restart:
```bash
tmux kill-server  # Kill all tmux sessions
# Then recreate using commands above
```

## ✅ Success Indicators

You'll know it's working when:
- `tmux ls` shows active sessions
- `status.sh` shows increasing supplier count
- Log file shows continuous activity
- Database reaches 23,206 suppliers

## 🎉 Final Result

After 2-3 hours:
- All 23,206 suppliers imported
- Each with AI-enhanced product catalogs
- Your "superbrain commerce" database ready!
- Can close laptop, check from iPhone anytime

**Remember:** Once started, you can safely disconnect. The import continues on Azure!