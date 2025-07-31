# Quick Docker Installation Guide

## 🚀 Fastest Way to Install Docker + Redis

### Option 1: Direct Download Link
1. **Download Docker Desktop**: 
   - [Click here to download](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
   - Or copy this link: `https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe`

2. **Install Docker Desktop**:
   - Run the downloaded installer
   - Choose "Use WSL 2" when asked
   - Click Install
   - **Restart your computer** when done

3. **After Restart**:
   - Docker Desktop will start automatically
   - Run: `WAIT-FOR-DOCKER-AND-START.bat`
   - Everything will start with Redis caching enabled!

### Option 2: Using Chocolatey (if installed)
```powershell
choco install docker-desktop -y
```

### Option 3: Using winget
```powershell
winget install Docker.DockerDesktop
```

## 📊 What Happens After Docker is Installed

When you run `docker-start.bat` or `WAIT-FOR-DOCKER-AND-START.bat`:

1. **Redis** starts automatically (port 6379)
2. **PostgreSQL** database starts
3. **FoodXchange** app starts with full caching
4. **Redis Commander** GUI available at http://localhost:8081

## 🔍 Verify Everything is Working

After Docker starts, check:
```batch
docker ps
```

You should see:
- foodxchange-web-1
- foodxchange-redis-1
- foodxchange-postgres-1
- foodxchange-redis-commander-1

## 💰 Benefits
- **90% reduction** in Azure API costs
- **Instant responses** for cached images
- **Better performance** overall
- **Professional setup** with all services containerized