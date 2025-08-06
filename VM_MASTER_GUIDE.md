# FoodXchange VM Master Guide

## 🖥️ Virtual Machine Details

### Current VM (Poland Central)
- **Name**: fdx-poland-vm
- **IP Address**: 74.248.141.31
- **Location**: Poland Central
- **Resource Group**: fdx-prod-rg
- **Size**: Standard_B2s (2 vCPUs, 4 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **User**: azureuser

### Performance Benefits
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Monthly Cost**: $57 (saving $3/month)
- **Network**: Optimized for European traffic

## 🌐 Application Access

### Main Services
- **Main App**: http://74.248.141.31 (port 80)
- **API Endpoint**: http://74.248.141.31:8000
- **Email CRM**: http://74.248.141.31:8003
- **Monitoring**: http://74.248.141.31:3000 (Grafana)

### Database
- **Server**: fdx-poland-db.postgres.database.azure.com
- **Database**: foodxchange
- **Connection**: `postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require`

## 🔑 SSH Access Configuration

### SSH Config Setup
Add to your `~/.ssh/config`:

```
Host fdx-poland
    HostName 74.248.141.31
    User azureuser
    IdentityFile ~/.ssh/fdx_poland_key
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Quick Connect
```bash
# Direct connection
ssh azureuser@74.248.141.31

# Using config
ssh fdx-poland

# With key file
ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31
```

## 🛠️ System Management

### Service Management
```bash
# Check all services
sudo systemctl status gunicorn nginx postgresql

# Restart application
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# View logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

### Resource Monitoring
```bash
# System resources
htop
df -h
free -h

# Network
netstat -tulpn
ss -tulpn
```

### Application Logs
```bash
# Application logs
sudo tail -f /var/log/foodxchange/app.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u gunicorn --since "1 hour ago"
```

## 📊 Monitoring & Health Checks

### Health Check URLs
- **Application**: http://74.248.141.31:8000/health
- **Database**: Check connection via psql
- **Services**: `sudo systemctl status`

### Monitoring Tools
- **Grafana**: http://74.248.141.31:3000
- **Netdata**: http://74.248.141.31:19999
- **System**: `htop`, `df -h`, `free -h`

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Service Not Responding
```bash
# Check service status
sudo systemctl status gunicorn nginx

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Check logs
sudo journalctl -u gunicorn --since "10 minutes ago"
```

#### 2. Database Connection Issues
```bash
# Test database connection
psql "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Check if database is accessible
nc -zv fdx-poland-db.postgres.database.azure.com 5432
```

#### 3. High Resource Usage
```bash
# Check CPU and memory
htop
free -h

# Check disk space
df -h

# Check running processes
ps aux --sort=-%cpu | head -10
```

#### 4. Network Issues
```bash
# Test connectivity
ping 74.248.141.31
curl http://74.248.141.31:8000/health

# Check open ports
netstat -tulpn | grep :8000
```

## 🚀 Deployment & Updates

### Code Deployment
```bash
# Pull latest code
cd /home/azureuser/foodxchange
git pull origin main

# Install dependencies
pip3 install -r requirements.txt

# Restart application
sudo systemctl restart gunicorn
```

### Configuration Updates
```bash
# Update environment variables
sudo nano /etc/foodxchange/.env

# Reload configuration
sudo systemctl reload gunicorn
```

### Database Updates
```bash
# Run migrations
python3 migrate_database.py

# Backup database
pg_dump "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require" > backup_$(date +%Y%m%d).sql
```

## 🔒 Security

### SSH Key Management
```bash
# Generate new key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/fdx_poland_key

# Copy public key to server
ssh-copy-id -i ~/.ssh/fdx_poland_key.pub azureuser@74.248.141.31

# Remove old keys from known_hosts
ssh-keygen -R 74.248.141.31
```

### Firewall Rules
```bash
# Check firewall status
sudo ufw status

# Allow specific ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 📈 Performance Optimization

### Current Optimizations
- Response caching (1-hour TTL)
- Database query optimization
- Static file serving via Nginx
- Gunicorn worker processes

### Monitoring Commands
```bash
# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s http://74.248.141.31:8000/

# Monitor database queries
sudo tail -f /var/log/postgresql/postgresql-*.log

# Check memory usage
free -h && echo "---" && cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable"
```

## 🆘 Emergency Procedures

### Immediate Actions
1. **Service Down**: `sudo systemctl restart gunicorn`
2. **Database Issues**: Check connection and restart if needed
3. **High Load**: Monitor with `htop` and restart services
4. **Disk Full**: Clean logs and temporary files

### Backup & Recovery
```bash
# Create backup
pg_dump "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require" > emergency_backup.sql

# Restore if needed
psql "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require" < emergency_backup.sql
```

## 📞 Quick Reference

### Essential Commands
```bash
# Connect to VM
ssh azureuser@74.248.141.31

# Check application
curl http://74.248.141.31:8000/health

# Monitor system
htop

# View logs
sudo journalctl -u gunicorn -f

# Restart everything
sudo systemctl restart gunicorn nginx
```

### Important URLs
- **Application**: http://74.248.141.31
- **API**: http://74.248.141.31:8000
- **Email CRM**: http://74.248.141.31:8003
- **Monitoring**: http://74.248.141.31:3000