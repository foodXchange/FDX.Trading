# iPhone SSH - FREE Quick Commands (No Snippets Needed!)

## 🎯 Method 1: Create Bash Aliases (Best Free Option)

After connecting to VM, run this ONCE:

```bash
# Add shortcuts to your profile
cat >> ~/.bashrc << 'EOF'

# FoodXchange Quick Commands
alias status='cd ~/foodxchange && ./status.sh'
alias import='tmux attach -t import'
alias count='cd ~/foodxchange && python3 check_progress.py'
alias logs='tail -30 ~/foodxchange/ai_import.log'
alias recent='cd ~/foodxchange && python3 -c "import psycopg2, os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv(\"DATABASE_URL\")); cur = conn.cursor(); cur.execute(\"SELECT COUNT(*) FROM suppliers WHERE created_at > NOW() - INTERVAL \\\"5 minutes\\\"\"); print(f\"Last 5 min: {cur.fetchone()[0]} suppliers\")"'

# Even shorter
alias s='status'
alias i='import'
alias c='count'
alias l='logs'
EOF

# Reload profile
source ~/.bashrc
```

Now you can just type:
- `s` - Full status
- `i` - View import
- `c` - Quick count
- `l` - Recent logs

## 🎯 Method 2: Create Simple Scripts

```bash
# Create a commands folder
mkdir -p ~/commands
cd ~/commands

# Status script
echo 'cd ~/foodxchange && ./status.sh' > s
chmod +x s

# Import viewer
echo 'tmux attach -t import' > i
chmod +x i

# Count script
echo 'cd ~/foodxchange && python3 check_progress.py' > c
chmod +x c

# Add to PATH
echo 'export PATH=$PATH:~/commands' >> ~/.bashrc
source ~/.bashrc
```

## 🎯 Method 3: iPhone Keyboard Shortcuts

### Set up iOS Text Replacements:
1. iPhone Settings → General → Keyboard → Text Replacement
2. Add these:

**Shortcut:** `;;status`
**Phrase:** `cd ~/foodxchange && ./status.sh`

**Shortcut:** `;;import`
**Phrase:** `tmux attach -t import`

**Shortcut:** `;;count`
**Phrase:** `cd ~/foodxchange && python3 check_progress.py`

Now in Termius, type `;;status` and it auto-expands!

## 🎯 Method 4: Copy-Paste Commands

Save these in iPhone Notes app:

```
=== CHECK STATUS ===
cd ~/foodxchange && ./status.sh

=== VIEW IMPORT ===
tmux attach -t import

=== QUICK COUNT ===
cd ~/foodxchange && python3 check_progress.py

=== RECENT ACTIVITY ===
cd ~/foodxchange && tail -20 ai_import.log | grep -E "(Imported:|Enhanced:)"

=== EXIT TMUX ===
Ctrl+B then D
```

## 📱 Fastest Workflow (No Payment!)

1. Connect to VM in Termius
2. Type one letter + Enter:
   - `s` → Full status
   - `i` → Watch import
   - `c` → Supplier count
   - `l` → Logs

That's it! No premium needed!

## 🚀 One-Time Setup Command

Copy this entire block and paste after connecting:

```bash
echo 'alias s="cd ~/foodxchange && ./status.sh"' >> ~/.bashrc && echo 'alias i="tmux attach -t import"' >> ~/.bashrc && echo 'alias c="cd ~/foodxchange && python3 check_progress.py"' >> ~/.bashrc && echo 'alias l="tail -20 ~/foodxchange/ai_import.log"' >> ~/.bashrc && source ~/.bashrc && echo "✅ Quick commands ready! Use: s, i, c, or l"
```

## 💡 Extra iPhone Tips

1. **Termius Toolbar:**
   - Swipe up from bottom
   - Common keys available
   - Tab, Ctrl, Esc easy access

2. **Copy Output:**
   - Long press on screen
   - Select text
   - Copy to clipboard

3. **Quick Reconnect:**
   - Termius remembers sessions
   - Just tap to reconnect

You now have FREE quick commands that are even faster than paid snippets! 🎉