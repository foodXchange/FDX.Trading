# Update DNS to New VM (Poland Central)

## Current DNS Configuration

### A Records
| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 74.248.141.31 | 300 |
| A | www | 74.248.141.31 | 300 |

### CNAME Records
| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | api | fdx.trading | 300 |

## DNS Provider: Cloudflare

### Steps to Update DNS

1. **Login to Cloudflare**
   - Go to https://dash.cloudflare.com
   - Select domain: `fdx.trading`

2. **Navigate to DNS Settings**
   - Click "DNS" in the left sidebar
   - Go to "Records" tab

3. **Update A Records**
   - Find the A record for `@` (root domain)
   - Change IP from old to: `74.248.141.31`
   - Find the A record for `www`
   - Change IP from old to: `74.248.141.31`
   - Save changes

4. **Verify Changes**
   ```bash
   # Test DNS resolution
   nslookup fdx.trading
   nslookup www.fdx.trading
   
   # Should show: Address: 74.248.141.31
   ```

## SSL Certificate

### Current Status
- **Provider**: Cloudflare
- **Type**: Universal SSL (Free)
- **Status**: Active
- **Coverage**: *.fdx.trading

### SSL Configuration
- **SSL/TLS Mode**: Full (strict)
- **Minimum TLS Version**: 1.2
- **HSTS**: Enabled
- **Security Level**: Medium

## Performance Benefits

### Poland Central Location
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Network**: Optimized for European traffic
- **Global CDN**: Cloudflare edge locations

### DNS Performance
- **TTL**: 300 seconds (5 minutes)
- **Propagation**: Usually 5-15 minutes
- **Global**: Cloudflare's worldwide network

## Testing DNS Update

### Command Line Testing
```bash
# Test root domain
dig fdx.trading
nslookup fdx.trading

# Test www subdomain
dig www.fdx.trading
nslookup www.fdx.trading

# Test from different locations
curl -I http://fdx.trading
curl -I https://www.fdx.trading
```

### Online Tools
- **DNS Checker**: https://dnschecker.org
- **What's My DNS**: https://www.whatsmydns.net
- **Cloudflare Status**: https://www.cloudflarestatus.com

## Troubleshooting

### Common Issues

1. **DNS Not Updated**
   - Wait 5-15 minutes for propagation
   - Clear local DNS cache: `ipconfig /flushdns` (Windows)
   - Try different DNS servers

2. **SSL Certificate Issues**
   - Check Cloudflare SSL/TLS settings
   - Ensure "Full (strict)" mode is enabled
   - Verify certificate is active

3. **Website Not Loading**
   - Check if VM is running: `ping 74.248.141.31`
   - Verify services are running on VM
   - Check firewall settings

### Verification Commands
```bash
# Test connectivity
ping 74.248.141.31

# Test web server
curl -I http://74.248.141.31

# Test SSL
openssl s_client -connect fdx.trading:443 -servername fdx.trading
```

## Monitoring

### DNS Health Checks
- **Uptime**: Monitor via Cloudflare
- **Response Time**: Track via Cloudflare Analytics
- **SSL Status**: Monitor certificate expiration

### Alerts Setup
- **DNS Failures**: Cloudflare notifications
- **SSL Issues**: Certificate expiration alerts
- **Performance**: Response time monitoring

## Future Considerations

### Scaling Options
1. **Load Balancer**: Multiple VM instances
2. **CDN**: Enhanced Cloudflare features
3. **Geographic Routing**: Route to nearest server

### Security Enhancements
1. **DDoS Protection**: Cloudflare Pro
2. **Bot Management**: Advanced security rules
3. **Rate Limiting**: API protection