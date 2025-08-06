# FoodXchange Infrastructure Documentation

## 🏗️ Current Infrastructure (Poland Central)

### Virtual Machine
- **Name**: fdx-poland-vm
- **IP Address**: 74.248.141.31
- **Location**: Poland Central
- **Resource Group**: fdx-prod-rg
- **Size**: Standard_B2s (2 vCPUs, 4 GB RAM)
- **OS**: Ubuntu 22.04 LTS

### Database
- **Server**: fdx-poland-db.postgres.database.azure.com
- **Database**: foodxchange
- **Location**: Poland Central
- **Resource Group**: fdx-data-rg
- **Connection String**: `postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require`

### Services & Ports

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Main Application | 8000 | http://74.248.141.31:8000 | ✅ Running |
| Web Server (Nginx) | 80 | http://74.248.141.31 | ✅ Running |
| Email CRM System | 8003 | http://74.248.141.31:8003 | ✅ Running |
| Grafana Monitoring | 3000 | http://74.248.141.31:3000 | ✅ Running |
| Netdata Monitoring | 19999 | http://74.248.141.31:19999 | ✅ Running |

### Resource Groups

#### fdx-prod-rg (Poland Central)
- fdx-poland-vm (Virtual Machine)
- Network Security Group
- Public IP Address

#### fdx-data-rg (Poland Central)
- fdx-poland-db (PostgreSQL Database)

#### fdx-trading-rg (Canada Central)
- SSL Certificate for fdx.trading domain

## 🔧 Access & Management

### SSH Access
```bash
# Connect to VM
ssh azureuser@74.248.141.31

# With key file
ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31
```

### Database Access
```bash
# Connect to PostgreSQL
psql "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"
```

### Application Management
```bash
# Check application status
sudo systemctl status gunicorn
sudo systemctl status nginx

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# View logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

## 📊 Performance & Monitoring

### Current Performance
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Database Size**: ~2GB
- **Monthly Cost**: $57 (saving $3/month vs US East)

### Monitoring Tools
1. **Grafana**: http://74.248.141.31:3000
   - System metrics
   - Application performance
   - Database queries

2. **Netdata**: http://74.248.141.31:19999
   - Real-time system monitoring
   - Resource usage

3. **Application Logs**
   - `/var/log/foodxchange/`
   - `sudo journalctl -u gunicorn`

## 🚀 Deployment & Updates

### Quick Access Commands
```bash
# Access VM
ssh azureuser@74.248.141.31

# Check application
curl http://74.248.141.31:8000/health

# Monitor resources
htop
df -h
free -h
```

### Backup & Recovery
1. **Database Backup**: Automated daily backups
2. **Application Backup**: Git repository
3. **Configuration Backup**: Stored in `/etc/foodxchange/`

## 🔒 Security

### Network Security
- Firewall rules configured
- SSH key-based authentication
- SSL/TLS encryption for database
- Regular security updates

### Access Control
- Limited SSH access
- Database connection restrictions
- Application-level authentication

## 📈 Scaling & Optimization

### Current Optimizations
- Response caching (1-hour TTL)
- Database query optimization
- Static file serving via Nginx
- Gunicorn worker processes

### Future Improvements
1. **Load Balancing**: Add multiple instances
2. **CDN**: CloudFlare integration
3. **Auto-scaling**: Based on traffic
4. **Monitoring**: Enhanced alerting

## 🛠️ Troubleshooting

### Common Issues
1. **Service Down**: Check systemctl status
2. **High CPU**: Monitor with htop
3. **Database Issues**: Check connection and logs
4. **Memory Issues**: Check free -h

### Support Commands
```bash
# Check all services
sudo systemctl status gunicorn nginx postgresql

# View recent logs
sudo journalctl -u gunicorn --since "1 hour ago"

# Check disk space
df -h

# Check memory usage
free -h

# Monitor real-time
htop
```

## 📞 Emergency Contacts

### Immediate Actions
1. **Service Restart**: `sudo systemctl restart gunicorn`
2. **Database Check**: `sudo systemctl status postgresql`
3. **Network Check**: `ping 74.248.141.31`

### Monitoring
1. **Application**: Check Grafana dashboard regularly at http://74.248.141.31:3000
2. **System**: Monitor Netdata at http://74.248.141.31:19999
3. **Logs**: Review application logs daily