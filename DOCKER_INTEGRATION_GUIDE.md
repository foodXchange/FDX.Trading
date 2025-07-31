# Docker Integration Guide for FoodXchange Development 🐳

## Overview
This guide sets up professional Docker integration in Cursor IDE for FoodXchange development, keeping Docker useful while preventing it from being intrusive.

## ✅ What's Configured

### 1. Professional Docker Settings
- **No Docker startup page** - Cursor opens to your project files
- **Show only running containers** - Reduces clutter
- **FoodXchange container filtering** - Only shows relevant containers
- **Optimized refresh intervals** - Better performance

### 2. Workspace Configuration
- **Cursor workspace file** - `foodxchange.code-workspace`
- **Docker workspace config** - `.cursor/docker-workspace.json`
- **Optimized settings** - `.cursor/settings.json`

### 3. Quick Actions
- **Launch script** - `launch-cursor.sh`
- **Fix script** - `fix-docker-integration.sh`
- **Restart script** - `restart-cursor.sh`

## 🚀 Quick Start

### Option 1: Use Launch Script (Recommended)
```bash
cd workspaces/FoodXchange
./launch-cursor.sh
```

### Option 2: Manual Launch
```bash
cd workspaces/FoodXchange
cursor foodxchange.code-workspace
```

### Option 3: Fix Issues
```bash
cd workspaces/FoodXchange
./fix-docker-integration.sh
```

## ⚙️ Docker Desktop Configuration

### Startup Behavior
1. Open Docker Desktop
2. Go to **Settings → General**
3. **Uncheck**: "Start Docker Desktop when you log in"
4. **Uncheck**: "Open Docker Dashboard at startup"
5. **Check**: "Use Docker Compose V2"

### Resource Limits
1. Go to **Settings → Resources**
2. Set **Memory**: 4GB (adjust based on your system)
3. Set **CPUs**: 2-4 cores
4. Set **Swap**: 1GB
5. Set **Disk Image Size**: 64GB

## 🎯 Expected Results

After applying these settings:

✅ **Cursor opens to your project files** (not Docker info)
✅ **Docker sidebar is available but not intrusive**
✅ **Only FoodXchange containers are shown**
✅ **Python environment is automatically activated**
✅ **Clean, focused development environment**

## 🔧 Troubleshooting

### If Cursor keeps opening Docker info:
```bash
# 1. Reset Cursor workspace
rm -rf .cursor/workspace.json

# 2. Clear Docker extension state
# In Cursor: Ctrl+Shift+P → "Developer: Reload Window"

# 3. Run fix script
./fix-docker-integration.sh

# 4. Restart Cursor
./restart-cursor.sh
```

### If Docker containers don't show:
1. Check if Docker is running: `docker info`
2. Verify container labels in `docker-compose.yml`
3. Ensure containers have the label: `com.foodxchange.service`

### If Python environment issues:
```bash
# Recreate virtual environment
rm -rf foodxchange-env
python3 -m venv foodxchange-env
source foodxchange-env/bin/activate
pip install -r requirements.txt
```

## 📋 Key Settings Explained

### Docker Control Settings
```json
{
  "docker.showStartPage": false,           // No Docker startup page
  "docker.containers.showRunningContainersOnly": true,  // Only running containers
  "docker.containers.label": "com.foodxchange.service",  // Filter by label
  "docker.explorerRefreshInterval": 5000   // Refresh every 5 seconds
}
```

### Startup Behavior
```json
{
  "workbench.startupEditor": "readme",     // Open to README, not Docker
  "window.restoreWindows": "one"           // Single window on startup
}
```

### File Exclusions
```json
{
  "files.exclude": {
    "**/docker-compose.override.yml": true,  // Hide override files
    "**/.dockerignore": false               // Show .dockerignore
  }
}
```

## 🎮 Available Tasks

In Cursor IDE, press `Ctrl+Shift+P` and type "Tasks: Run Task" to access:

- **Start FoodXchange** - Runs `./fx.bat`
- **Start Docker Services** - Runs `docker-compose up -d`
- **Stop Docker Services** - Runs `docker-compose down`
- **Docker Logs** - Shows `docker-compose logs -f`

## 🔍 Container Labels

For containers to show in the filtered view, ensure your `docker-compose.yml` includes:

```yaml
services:
  web:
    labels:
      - "com.foodxchange.service=web"
  redis:
    labels:
      - "com.foodxchange.service=redis"
  nginx:
    labels:
      - "com.foodxchange.service=nginx"
```

## 📱 Keyboard Shortcuts

- `Ctrl+Shift+E` - Open Docker explorer
- `Ctrl+Shift+P` - Command palette
- `Ctrl+Shift+\`` - Integrated terminal
- `Ctrl+Shift+B` - Run build tasks

## 🎉 Success Indicators

You'll know it's working when:

1. **Cursor opens to README.md** instead of Docker info
2. **Docker sidebar shows only FoodXchange containers**
3. **Terminal automatically activates Python environment**
4. **No Docker startup page appears**
5. **Clean, focused development environment**

## 🆘 Emergency Recovery

If everything breaks:

```bash
# 1. Stop all containers
docker-compose down

# 2. Reset Cursor settings
rm -rf .cursor/
./fix-docker-integration.sh

# 3. Restart Docker Desktop
# 4. Restart Cursor IDE
./restart-cursor.sh
```

---

**Bottom Line**: Docker integration is useful for FoodXchange development - just need to configure it to be helpful, not intrusive! 🎉
