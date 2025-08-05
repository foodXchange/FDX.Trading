# iPhone + Azure VM + Claude Setup

## Quick Setup for iPhone Access

### 1. On iPhone - Install Termius
- App Store → Search "Termius" → Install (free)
- Add new host:
  - **Alias:** FoodX VM
  - **Hostname:** 4.206.1.15
  - **Username:** azureuser
  - **Password:** FDX2025!Import#VM

### 2. On VM - Set Up Persistent Sessions
```bash
# Connect from iPhone
ssh azureuser@4.206.1.15

# Install tmux
sudo apt install tmux

# Create named sessions
tmux new -s import    # For import tasks
tmux new -s claude    # For Claude work
tmux new -s monitor   # For monitoring

# Detach: Ctrl+B then D
# List sessions: tmux ls
# Attach: tmux attach -t import
```

### 3. Run Import in Background
```bash
# In tmux session "import"
tmux attach -t import
cd ~/foodxchange
python3 import.py

# Detach (Ctrl+B, D) - it keeps running!
# Close iPhone - still running!
```

### 4. Check Progress from iPhone Anytime
```bash
# Quick check (30 seconds)
ssh azureuser@4.206.1.15
tmux attach -t import
# See progress
# Detach and close
```

## Your Daily Workflow

**Morning (iPhone - 1 min)**
- Open Termius
- Connect to VM
- `tmux ls` - see what's running
- Check import progress

**Anytime (iPhone - 2 min)**
- Quick database checks
- Monitor operations
- Fix urgent issues

**Evening (Computer - when convenient)**
- Full development work
- Start long operations
- Leave running overnight

## Pro Tips for iPhone

1. **Save SSH Key in Termius**
   - More secure than password
   - Faster login

2. **Create Shortcuts**
   ```bash
   # Add to ~/.bashrc
   alias check='tmux attach -t import'
   alias db='python3 -c "import psycopg2; ..."'
   ```

3. **Use Landscape Mode**
   - Better for coding
   - More screen space

## Complete Freedom!
- ✅ Import runs without your computer
- ✅ Check progress from anywhere
- ✅ Never lose work (tmux persists)
- ✅ Total cost: ~$10/month (VM only)

Your suppliers will import while you sleep, travel, or work on other things!