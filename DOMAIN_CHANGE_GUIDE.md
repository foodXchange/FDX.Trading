# Domain Change Guide: Azure to fdx.trading (Namecheap)

## Current Azure Services Status

✅ **Azure App Service**: `foodxchange-app` (West Europe)  
✅ **Current URL**: https://foodxchange-app.azurewebsites.net  
✅ **Resource Group**: `foodxchange-rg`  
✅ **App Service Plan**: `foodxchange-plan`  

## Step-by-Step Domain Change Process

### 1. **Namecheap Domain Configuration**

#### A. DNS Records Setup in Namecheap

1. **Login to Namecheap** and go to your domain `fdx.trading`
2. **Go to "Advanced DNS"** section
3. **Add these DNS records**:

```
Type: CNAME
Name: @
Value: foodxchange-app.azurewebsites.net
TTL: Automatic

Type: CNAME  
Name: www
Value: foodxchange-app.azurewebsites.net
TTL: Automatic
```

#### B. Alternative: A Record Setup (Recommended)

If you want better performance, use A records:

```
Type: A
Name: @
Value: [Azure App Service IP - we'll get this]
TTL: Automatic

Type: CNAME
Name: www
Value: fdx.trading
TTL: Automatic
```

### 2. **Azure App Service Configuration**

#### A. Add Custom Domain to Azure

```powershell
# Add the custom domain
az webapp config hostname add --webapp-name foodxchange-app --resource-group foodxchange-rg --hostname fdx.trading

# Add www subdomain
az webapp config hostname add --webapp-name foodxchange-app --resource-group foodxchange-rg --hostname www.fdx.trading
```

#### B. Get Azure App Service IP (for A records)

```powershell
# Get the outbound IP addresses
az webapp show --name foodxchange-app --resource-group foodxchange-rg --query outboundIpAddresses --output tsv
```

### 3. **SSL Certificate Setup**

#### A. Azure App Service Managed Certificate (Free)

```powershell
# Enable managed certificate for custom domain
az webapp config ssl bind --certificate-thumbprint [thumbprint] --ssl-type SNI --name foodxchange-app --resource-group foodxchange-rg --hostname fdx.trading
```

#### B. Alternative: Upload Custom Certificate

1. **Purchase SSL certificate** from Namecheap or other provider
2. **Upload to Azure**:
   ```powershell
   az webapp config ssl upload --certificate-file path/to/cert.pfx --certificate-password [password] --name foodxchange-app --resource-group foodxchange-rg
   ```

### 4. **Environment Variables Update**

Update your Azure App Service configuration:

```powershell
# Update CORS origins to include new domain
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings BACKEND_CORS_ORIGINS="https://fdx.trading,https://www.fdx.trading"

# Update email settings if needed
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings EMAILS_FROM_EMAIL="noreply@fdx.trading"
```

### 5. **Application Code Updates**

#### A. Update CORS Configuration

In your `app/config.py` or main application file:

```python
# Update CORS origins
BACKEND_CORS_ORIGINS = [
    "https://fdx.trading",
    "https://www.fdx.trading",
    "http://localhost:3000",  # Keep for development
    "http://localhost:8000"   # Keep for development
]
```

#### B. Update Email Templates

Update any hardcoded URLs in your email templates to use `fdx.trading`.

### 6. **Testing and Verification**

#### A. DNS Propagation Check

```bash
# Check if DNS is propagating
nslookup fdx.trading
nslookup www.fdx.trading
```

#### B. SSL Certificate Verification

```bash
# Check SSL certificate
openssl s_client -connect fdx.trading:443 -servername fdx.trading
```

#### C. Application Testing

1. **Test main domain**: https://fdx.trading
2. **Test www subdomain**: https://www.fdx.trading
3. **Test SSL redirects**: http://fdx.trading → https://fdx.trading
4. **Test all application features** with new domain

### 7. **Redirects Setup (Optional but Recommended)**

#### A. Azure App Service Redirect Rules

Add to your `web.config` file:

```xml
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <!-- Redirect www to non-www -->
        <rule name="Redirect www to non-www" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTP_HOST}" pattern="^www\.fdx\.trading$" />
          </conditions>
          <action type="Redirect" url="https://fdx.trading/{R:1}" redirectType="Permanent" />
        </rule>
        
        <!-- Redirect HTTP to HTTPS -->
        <rule name="Redirect HTTP to HTTPS" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTPS}" pattern="off" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### 8. **Monitoring and Maintenance**

#### A. Set up Monitoring

```powershell
# Enable application logging
az webapp log config --name foodxchange-app --resource-group foodxchange-rg --application-logging filesystem --level information

# Enable detailed error logging
az webapp config set --name foodxchange-app --resource-group foodxchange-rg --detailed-error-logging true
```

#### B. Set up Alerts

1. **Go to Azure Portal** → Your App Service → Monitoring → Alerts
2. **Create alert rules** for:
   - Response time > 2 seconds
   - HTTP 5xx errors
   - CPU usage > 80%
   - Memory usage > 80%

### 9. **Backup and Rollback Plan**

#### A. Backup Current Configuration

```powershell
# Export current app settings
az webapp config appsettings list --name foodxchange-app --resource-group foodxchange-rg --output json > app-settings-backup.json

# Export current hostname bindings
az webapp config hostname list --webapp-name foodxchange-app --resource-group foodxchange-rg --output json > hostname-bindings-backup.json
```

#### B. Rollback Procedure

If something goes wrong:

```powershell
# Remove custom domain
az webapp config hostname delete --webapp-name foodxchange-app --resource-group foodxchange-rg --hostname fdx.trading

# Restore original settings
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
```

## Quick Setup Script

Create `setup_custom_domain.ps1`:

```powershell
# Quick setup script for fdx.trading domain
$resourceGroup = "foodxchange-rg"
$appName = "foodxchange-app"
$domain = "fdx.trading"
$wwwDomain = "www.fdx.trading"

Write-Host "Setting up custom domain: $domain" -ForegroundColor Green

# Add custom domains
az webapp config hostname add --webapp-name $appName --resource-group $resourceGroup --hostname $domain
az webapp config hostname add --webapp-name $appName --resource-group $resourceGroup --hostname $wwwDomain

# Update CORS settings
az webapp config appsettings set --name $appName --resource-group $resourceGroup --settings BACKEND_CORS_ORIGINS="https://$domain,https://$wwwDomain"

# Get outbound IPs for DNS A records
Write-Host "`nOutbound IP addresses for A records:" -ForegroundColor Yellow
az webapp show --name $appName --resource-group $resourceGroup --query outboundIpAddresses --output tsv

Write-Host "`nSetup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Configure DNS records in Namecheap" -ForegroundColor White
Write-Host "2. Wait for DNS propagation (up to 48 hours)" -ForegroundColor White
Write-Host "3. Test the new domain" -ForegroundColor White
```

## Timeline

- **DNS Setup**: 5 minutes
- **Azure Configuration**: 10 minutes  
- **DNS Propagation**: 15 minutes to 48 hours
- **SSL Certificate**: 5-10 minutes (managed) or 1-2 hours (custom)
- **Testing**: 30 minutes
- **Total**: 1-2 hours (excluding DNS propagation)

## Cost Impact

- **Azure App Service**: No additional cost
- **Custom Domain**: No additional cost
- **Managed SSL Certificate**: Free
- **Custom SSL Certificate**: $10-50/year (if purchased)
- **Total Additional Cost**: $0-50/year

## Support

If you encounter issues:

1. **Check DNS propagation**: https://www.whatsmydns.net/
2. **Verify SSL certificate**: https://www.ssllabs.com/ssltest/
3. **Check Azure App Service logs**: Azure Portal → App Service → Log stream
4. **Contact Azure Support**: If technical issues persist

## Next Steps After Domain Change

1. **Update all internal links** to use fdx.trading
2. **Update email signatures** and business cards
3. **Update social media profiles** and listings
4. **Set up Google Search Console** for the new domain
5. **Configure Google Analytics** for the new domain
6. **Update any third-party integrations** that reference the old domain 