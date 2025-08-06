# FoodXchange VM Documentation

## 🖥️ Current Infrastructure (Poland Central)

### Virtual Machine Details
- **Name**: fdx-poland-vm
- **IP Address**: 74.248.141.31
- **Location**: Poland Central
- **Resource Group**: fdx-prod-rg
- **Size**: Standard_B2s (2 vCPUs, 4 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **User**: azureuser

### Database Details
- **Server**: fdx-poland-db.postgres.database.azure.com
- **Database**: foodxchange
- **Location**: Poland Central
- **Resource Group**: fdx-data-rg
- **Connection String**: `postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require`

## 🌐 Application Access

### Main Services
- **VM Dashboard**: http://74.248.141.31
- **Application**: http://74.248.141.31:8000
- **Email CRM**: http://74.248.141.31:8003
- **Grafana Monitoring**: http://74.248.141.31:3000
- **Netdata Monitoring**: http://74.248.141.31:19999

### SSH Access
```bash
# Connect to VM
ssh azureuser@74.248.141.31

# With SSH key
ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31
```

## 📊 Performance Benefits

### Poland Central Location
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Network**: Optimized for European traffic
- **Monthly Cost**: $57 (saving $3/month vs US East)

### Current Performance
- **Database Size**: ~2GB
- **Suppliers**: 17,771+ records
- **Response Time**: <200ms average
- **Uptime**: 99.9% target

## 🛠️ Quick Commands

### System Management
```bash
# Check services
sudo systemctl status gunicorn nginx

# Restart application
sudo systemctl restart gunicorn

# View logs
sudo journalctl -u gunicorn -f

# Monitor system
htop
df -h
free -h
```

### Database Operations
```bash
# Connect to database
psql "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Check supplier count
SELECT COUNT(*) FROM suppliers;

# Backup database
pg_dump "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require" > backup_$(date +%Y%m%d).sql
```

## 🔧 Troubleshooting

### Common Issues
1. **Service Down**: `sudo systemctl restart gunicorn`
2. **High CPU**: Monitor with `htop`
3. **Database Issues**: Check connection and logs
4. **Memory Issues**: Check with `free -h`

### Emergency Procedures
```bash
# Full system check
sudo systemctl status gunicorn nginx postgresql

# Recent logs
sudo journalctl -u gunicorn --since "1 hour ago"

# Resource usage
htop && df -h && free -h
```

## 📈 Monitoring

### Health Checks
- **Application**: http://74.248.141.31:8000/health
- **Database**: Test connection via psql
- **Services**: `sudo systemctl status`

### Monitoring Tools
- **Grafana**: http://74.248.141.31:3000
- **Netdata**: http://74.248.141.31:19999
- **System**: `htop`, `df -h`, `free -h`

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

## 🚀 Deployment

### GitHub Actions
- **Workflow**: `.github/workflows/deploy.yml`
- **Trigger**: Push to main branch
- **Target**: Poland Central VM
- **Health Check**: Automatic verification

### Manual Deployment
```bash
# Pull latest code
cd /home/azureuser/foodxchange
git pull origin main

# Install dependencies
pip3 install -r requirements.txt

# Restart application
sudo systemctl restart gunicorn
```

## 📞 Quick Reference

### Essential URLs
- **Application**: http://74.248.141.31
- **API**: http://74.248.141.31:8000
- **Email CRM**: http://74.248.141.31:8003
- **Monitoring**: http://74.248.141.31:3000

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

## 🎯 Migration Benefits

### Performance Improvements
- **Latency**: 200ms → 30ms (6x faster)
- **Network**: Optimized for European traffic
- **Cost**: $60 → $57/month (saving $3/month)

### Infrastructure Benefits
- **Reliability**: Better network connectivity
- **Scalability**: Optimized for European market
- **Monitoring**: Enhanced observability
- **Security**: Improved access controls

## 📋 Next Steps

### Immediate Actions
1. **DNS Update**: Point fdx.trading to 74.248.141.31
2. **SSL Setup**: Configure Cloudflare SSL
3. **Monitoring**: Set up alerts and notifications
4. **Backup**: Configure automated backups

### Future Improvements
1. **Load Balancing**: Add multiple VM instances
2. **CDN**: CloudFlare integration
3. **Auto-scaling**: Based on traffic patterns
4. **Enhanced Monitoring**: Application Insights setup