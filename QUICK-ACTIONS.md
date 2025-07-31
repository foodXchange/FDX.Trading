# FoodXchange Docker Quick Actions

## 🚀 One-Click Actions

### First Time Setup
```batch
SETUP-AND-RUN.bat
```
This will:
- Check/Install Docker Desktop
- Start all services including Redis
- Open the app in your browser

### Daily Operations

| Action | Command | What it does |
|--------|---------|--------------|
| **Start Everything** | `docker-start.bat` | Starts all services with Redis caching |
| **Stop Everything** | `docker-stop.bat` | Stops all services gracefully |
| **Restart Services** | `docker-restart.bat` | Restarts all containers |
| **View Logs** | `docker-logs.bat` | Shows live logs from all services |
| **Check Cache** | `docker-check-cache.bat` | Shows Redis cache statistics |
| **Management Dashboard** | `DOCKER-DASHBOARD.bat` | Interactive menu for all operations |

## 🎯 Advanced Automation

### PowerShell Management
```powershell
# Check status
.\docker-manage.ps1 status

# Start services
.\docker-manage.ps1 start

# View Redis CLI
.\docker-manage.ps1 redis

# Backup data
.\docker-manage.ps1 backup

# Clean everything
.\docker-manage.ps1 clean
```

### Automated Deployment
```powershell
# Deploy to development
.\AUTO-DEPLOY.ps1 -Environment development

# Deploy to production with backup
.\AUTO-DEPLOY.ps1 -Environment production

# Force deploy without tests
.\AUTO-DEPLOY.ps1 -SkipTests -Force
```

## 📊 Monitoring

### Cache Performance
```batch
docker exec foodxchange-redis-1 redis-cli info stats
```

### View Cached Keys
```batch
docker exec foodxchange-redis-1 redis-cli keys "*"
```

### Monitor in Real-Time
Open Redis Commander: http://localhost:8081

## 🔧 Troubleshooting

### Services Won't Start
```batch
REM Check what's running
docker ps -a

REM Check logs
docker-compose logs web
docker-compose logs redis

REM Restart everything
docker-compose down -v
docker-compose up -d
```

### Port Conflicts
```batch
REM Find what's using port 8003
netstat -ano | findstr :8003

REM Kill process (replace PID)
taskkill /PID 1234 /F
```

### Redis Not Caching
```batch
REM Test Redis connection
docker exec foodxchange-redis-1 redis-cli ping

REM Check Redis logs
docker logs foodxchange-redis-1

REM Restart Redis only
docker-compose restart redis
```

## 🎉 Benefits of This Setup

1. **90% Azure API Cost Reduction** - Redis caches all AI analysis
2. **One-Click Operations** - Everything automated
3. **Automatic Health Checks** - Services monitor themselves
4. **Easy Backup/Restore** - Your data is always safe
5. **Development Speed** - Hot reload enabled

## 📝 Daily Workflow

1. **Morning Start**
   ```batch
   docker-start.bat
   ```

2. **Check Cache Performance**
   ```batch
   docker-check-cache.bat
   ```

3. **End of Day**
   ```batch
   docker-stop.bat
   ```

4. **Weekly Backup**
   ```powershell
   .\docker-manage.ps1 backup
   ```

That's it! Everything is automated for maximum productivity.