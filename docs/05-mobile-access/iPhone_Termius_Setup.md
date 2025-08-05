# iPhone Termius Setup for Azure VM Access

## 📱 Step 1: Install Termius

1. Open **App Store** on iPhone
2. Search: **"Termius SSH"**
3. Download **Termius - SSH client** (free)
4. Open the app

## 🔧 Step 2: Add Your Azure VM

### Option A: Quick Setup (Recommended)

1. In Termius, tap **"+"** button
2. Select **"New Host"**
3. Fill in:
   - **Label/Alias:** `FoodX Azure VM`
   - **Hostname:** `4.206.1.15`
   - **Port:** `22` (default)
   - **Username:** `azureuser`
   - **Password:** `FDX2025!Import#VM`
4. Tap **Save** (top right)

### Option B: Even Quicker (Copy & Paste)

1. Copy this entire block:
   ```
   Host: 4.206.1.15
   User: azureuser
   Pass: FDX2025!Import#VM
   ```
2. In Termius → Hosts → Import

## 🚀 Step 3: Connect to VM

1. Tap on **"FoodX Azure VM"** from your hosts
2. Accept fingerprint (first time only)
3. You're connected! 🎉

## 📝 Step 4: Essential Commands

### Check Import Status (Copy these)
```bash
# Quick status
tmux attach -t import
# Press Ctrl+B then D to exit

# Database count
python3 -c "
import psycopg2, os
from dotenv import load_dotenv
os.chdir('/home/azureuser/foodxchange')
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM suppliers')
print(f'Suppliers: {cur.fetchone()[0]:,} / 23,206')
"
```

## 💡 Pro Tips for iPhone

### 1. Enable Touch/Face ID
- Settings → Security → Enable Biometric
- Faster login!

### 2. Create Snippets (Time Savers!)
1. In Termius: Settings → Snippets → Add
2. Create these snippets:

**"Status"**
```bash
cd ~/foodxchange && ./status.sh
```

**"Check Import"**
```bash
tmux attach -t import
```

**"Count"**
```bash
cd ~/foodxchange && python3 check_progress.py
```

### 3. Keyboard Shortcuts
- **Tab key:** Swipe right on keyboard
- **Ctrl key:** Tap `Ctrl` button
- **Arrow keys:** Swipe on terminal

### 4. Better Viewing
- **Landscape mode:** Rotate phone
- **Zoom:** Pinch to zoom
- **Font size:** Settings → Terminal → Font Size

## 🎯 Quick Actions Menu

After connecting, save these as "Quick Commands":

1. **"Import Status"**
   ```
   tmux attach -t import
   ```

2. **"Supplier Count"**
   ```
   cd ~/foodxchange && python3 -c "import psycopg2, os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM suppliers'); print(f'Total: {cur.fetchone()[0]:,}')"
   ```

3. **"View Logs"**
   ```
   tail -20 ~/foodxchange/ai_import.log
   ```

## 🔄 Daily Routine (30 seconds)

1. Open Termius
2. Tap "FoodX Azure VM"
3. Run snippet: "Status"
4. See results
5. Close app

## 🆘 Troubleshooting

### Can't connect?
- Check WiFi/cellular
- Verify IP: `4.206.1.15`
- Try again in 30 seconds

### Keyboard issues?
- Use Termius keyboard (bottom bar)
- Enable "Show extra keys"

### Session timeout?
- Normal! Just reconnect
- tmux sessions remain active

## 🎉 Success!

You can now:
- ✅ Check import progress from anywhere
- ✅ Monitor database growth
- ✅ Restart if needed
- ✅ All from your iPhone!

**Remember:** The import keeps running even when you're not connected. tmux is magic! 🪄