# iPhone VM Setup - Poland Central

## 📱 Quick Setup for iPhone

### 1. Download Termius (Free SSH App)
- Open App Store
- Search for "Termius"
- Download and install

### 2. Create SSH Connection

#### Connection Details:
- **Hostname:** 74.248.141.31
- **Username:** azureuser
- **Port:** 22
- **Authentication:** SSH Key

#### SSH Key Setup:
1. **Generate Key** (if you don't have one):
   ```bash
   # On your computer
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/fdx_poland_key
   ```

2. **Copy Public Key to VM**:
   ```bash
   ssh-copy-id -i ~/.ssh/fdx_poland_key.pub azureuser@74.248.141.31
   ```

3. **Add Key to Termius**:
   - Open Termius
   - Go to "Keys" tab
   - Tap "+" to add new key
   - Copy your private key content
   - Paste and save

### 3. Create Host in Termius

1. **Add New Host**:
   - Tap "+" in Termius
   - Choose "New Host"

2. **Fill Details**:
   - **Label:** FoodXchange VM
   - **Hostname:** 74.248.141.31
   - **Username:** azureuser
   - **Port:** 22
   - **Authentication:** SSH Key
   - **Key:** Select your fdx_poland_key

3. **Save and Connect**:
   - Tap "Save"
   - Tap the connection to connect

## 🚀 Quick Commands

### Essential Commands (Save as Snippets)
```bash
# Check system status
sudo systemctl status gunicorn nginx

# Restart application
sudo systemctl restart gunicorn

# View logs
sudo journalctl -u gunicorn -f

# Monitor system
htop

# Check disk space
df -h

# Check memory
free -h
```

### Create Snippets in Termius:
1. Go to "Snippets" tab
2. Tap "+" to add new snippet
3. Create these snippets:

#### System Status
```bash
echo "=== SYSTEM STATUS ===" && \
sudo systemctl status gunicorn nginx --no-pager && \
echo "=== DISK SPACE ===" && \
df -h && \
echo "=== MEMORY ===" && \
free -h
```

#### Restart App
```bash
sudo systemctl restart gunicorn && echo "✅ App restarted"
```

#### View Logs
```bash
sudo journalctl -u gunicorn --since "10 minutes ago" --no-pager
```

## 🌐 Web Access

### Application URLs
- **Main App**: http://74.248.141.31
- **API**: http://74.248.141.31:8000
- **Email CRM**: http://74.248.141.31:8003
- **Monitoring**: http://74.248.141.31:3000

### Add to iPhone Home Screen:
1. Open Safari
2. Go to any of the URLs above
3. Tap the share button
4. Choose "Add to Home Screen"
5. Name it (e.g., "FoodXchange")

## 🔧 Troubleshooting

### Connection Issues
```bash
# Test connection
ping 74.248.141.31

# Check if VM is running
ssh azureuser@74.248.141.31 "echo 'VM is running'"
```

### App Not Responding
```bash
# Check if services are running
sudo systemctl status gunicorn nginx

# Restart if needed
sudo systemctl restart gunicorn nginx
```

### High Resource Usage
```bash
# Check CPU and memory
htop

# Kill high-CPU processes if needed
ps aux --sort=-%cpu | head -5
```

## 📊 Performance Benefits

### Poland Central Location
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Network**: Optimized for European traffic
- **Cost**: $57/month (saving $3/month)

### Mobile Optimization
- **Responsive Design**: Works great on iPhone
- **Fast Loading**: Optimized for mobile networks
- **Touch-Friendly**: Bootstrap UI components

## 🎯 Pro Tips

### 1. Use Split Screen (iPad)
- SSH in Termius on left
- Safari with app on right
- Perfect for development

### 2. Create Shortcuts
- Use iPhone Shortcuts app
- Create quick actions for common tasks
- One-tap app restart

### 3. Monitor Regularly
- Check system status daily
- Monitor disk space weekly
- Review logs when issues occur

### 4. Backup Strategy
- Regular database backups
- Configuration backups
- Document any changes

## 🔒 Security Notes

### SSH Key Security
- Keep private key secure
- Don't share keys
- Use passphrase protection
- Rotate keys periodically

### Network Security
- VM has firewall rules
- Only necessary ports open
- Regular security updates
- Monitor access logs

## 📞 Emergency Contacts

### Quick Fixes
1. **App Down**: `sudo systemctl restart gunicorn`
2. **High CPU**: `htop` then kill processes
3. **Disk Full**: `df -h` then clean up
4. **Memory Issues**: `free -h` then restart services

### When to Contact Support
- VM not responding to ping
- Database connection issues
- SSL certificate problems
- Performance degradation