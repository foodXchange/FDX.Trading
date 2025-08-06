# FoodXchange Quick Reference Card

## 🖥️ VM Details
- **VM IP**: `74.248.141.31`
- **SSH**: `ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31`
- **App**: http://74.248.141.31:8000
- **Location**: Poland Central

## 🔑 Quick Access
```bash
# Connect to VM
ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31

# Check app status
curl http://74.248.141.31:8000/health

# Monitor system
htop
```

## 🌐 Application URLs
- **Main App**: http://74.248.141.31
- **API**: http://74.248.141.31:8000
- **Email CRM**: http://74.248.141.31:8003
- **Monitoring**: http://74.248.141.31:3000

## 🗄️ Database
- **Server**: fdx-poland-db.postgres.database.azure.com
- **Connection**: `postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require`

## 🛠️ Service Management
```bash
# Check services
sudo systemctl status gunicorn nginx

# Restart app
sudo systemctl restart gunicorn

# View logs
sudo journalctl -u gunicorn -f
```

## 📊 Monitoring
- **Grafana**: http://74.248.141.31:3000
- **Netdata**: http://74.248.141.31:19999
- **System**: `htop`, `df -h`, `free -h`

## 🔧 Troubleshooting
```bash
# Service down
sudo systemctl restart gunicorn nginx

# High CPU
htop

# Disk space
df -h

# Memory
free -h
```

## 📈 Performance
- **Latency from Israel**: ~30ms
- **Monthly Cost**: $57
- **Database Size**: ~2GB

## 🚨 Emergency
1. **Service Restart**: `sudo systemctl restart gunicorn`
2. **Database Check**: Test connection via psql
3. **Network Check**: `ping 74.248.141.31`

## 📞 Quick Commands
```bash
# Full system check
sudo systemctl status gunicorn nginx postgresql

# Recent logs
sudo journalctl -u gunicorn --since "1 hour ago"

# Resource usage
htop && df -h && free -h
```