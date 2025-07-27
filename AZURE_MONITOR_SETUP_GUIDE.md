# Azure Monitor Setup Guide for Food Xchange

This guide will help you set up Azure Application Insights monitoring for your Food Xchange application.

## 🚀 Quick Start

### 1. Prerequisites
- Azure CLI installed and logged in
- Your Food Xchange app deployed to Azure App Service
- PowerShell available on your system

### 2. Automated Setup
Run the automated setup script:
```powershell
.\setup_azure_monitor.ps1
```

This script will:
- Check your Azure CLI installation
- Create Application Insights resource
- Generate configuration files
- Provide Azure Portal links

### 3. Manual Setup (Alternative)

If you prefer manual setup:

#### Step 1: Install Azure CLI Extension
```powershell
az extension add --name application-insights
```

#### Step 2: Create Application Insights
```powershell
az monitor app-insights component create `
    --app "foodxchange-insights" `
    --location eastus `
    --resource-group your-resource-group `
    --application-type web
```

#### Step 3: Get Instrumentation Key
```powershell
$instrumentationKey = az monitor app-insights component show `
    --app "foodxchange-insights" `
    --resource-group your-resource-group `
    --query instrumentationKey -o tsv
```

## 🔧 Configuration

### Environment Variables
Add these to your Azure App Service configuration:

```bash
AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY=your-instrumentation-key
AZURE_APP_INSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key;IngestionEndpoint=https://eastus-0.in.applicationinsights.azure.com/
AZURE_APP_INSIGHTS_ENABLED=true
```

### Azure App Service Configuration
1. Go to your App Service in Azure Portal
2. Navigate to Configuration > Application settings
3. Add the environment variables above
4. Save and restart your app

## 📊 Monitoring Features

### What Gets Monitored
- **Application Performance**: Response times, request rates
- **Errors & Exceptions**: Automatic error tracking
- **Dependencies**: Database calls, external API calls
- **Custom Events**: Business events and metrics
- **System Metrics**: CPU, memory, disk usage

### Available Endpoints
- `/health` - Basic health check with Azure Monitor status
- `/monitoring/azure` - Azure Monitor configuration status
- `/monitoring/test` - Test all monitoring systems
- `/metrics` - System performance metrics

## 🔍 System Monitoring

### Run System Monitor
```powershell
# Single check
.\system-monitor.ps1

# Continuous monitoring (every 30 seconds)
.\system-monitor.ps1 -Continuous -Interval 30

# Custom URL
.\system-monitor.ps1 -BaseUrl "https://your-app.azurewebsites.net"
```

### Or use the batch file
```cmd
run-system-monitor.bat
```

## 📈 Azure Portal Dashboard

### Access Your Data
1. Go to Azure Portal
2. Navigate to your Application Insights resource
3. View:
   - **Live Metrics**: Real-time application performance
   - **Application Map**: Service dependencies
   - **Performance**: Response times and bottlenecks
   - **Failures**: Error analysis and trends
   - **Logs**: Custom events and traces

### Key Metrics to Monitor
- **Response Time**: Should be under 500ms for most requests
- **Request Rate**: Monitor traffic patterns
- **Error Rate**: Should be under 1%
- **Dependency Performance**: Database and external API calls
- **System Resources**: CPU, memory, disk usage

## 🛠️ Troubleshooting

### Common Issues

#### 1. Azure Monitor Not Initializing
**Symptoms**: No Azure Monitor logs in Application Insights
**Solution**: 
- Check environment variables are set correctly
- Verify instrumentation key is valid
- Restart the application after configuration changes

#### 2. Dependencies Not Found
**Symptoms**: Import errors for opencensus packages
**Solution**:
```bash
pip install opencensus-ext-azure==1.1.12
pip install opencensus-ext-fastapi==0.1.0
```

#### 3. No Data in Azure Portal
**Symptoms**: Application Insights shows no data
**Solution**:
- Wait 5-10 minutes for data to appear
- Check if the app is generating traffic
- Verify connection string format
- Check firewall rules if applicable

### Debug Commands
```powershell
# Test Azure Monitor status
curl https://your-app.azurewebsites.net/monitoring/azure

# Test all monitoring systems
curl https://your-app.azurewebsites.net/monitoring/test

# Check health with monitoring status
curl https://your-app.azurewebsites.net/health
```

## 📋 Best Practices

### 1. Sampling Strategy
- Use 100% sampling in development
- Use 10-20% sampling in production for cost optimization
- Adjust based on traffic volume

### 2. Custom Events
Log important business events:
```python
azure_monitor.log_event("order_created", {
    "order_id": order.id,
    "customer_id": customer.id,
    "total_amount": order.total
})
```

### 3. Performance Monitoring
Monitor critical operations:
```python
with azure_monitor.start_span("database_query"):
    result = db.execute(query)
```

### 4. Error Tracking
Log exceptions with context:
```python
try:
    # Your code
except Exception as e:
    azure_monitor.log_exception(e, {
        "operation": "process_order",
        "order_id": order_id
    })
```

## 💰 Cost Optimization

### Azure Application Insights Pricing
- **Data Ingestion**: Pay per GB ingested
- **Data Retention**: 90 days included, additional retention costs extra
- **Live Metrics**: Included at no additional cost

### Cost Reduction Tips
1. **Enable Sampling**: Reduce data volume
2. **Filter Events**: Only log important events
3. **Set Data Retention**: Use shorter retention for non-critical data
4. **Monitor Usage**: Set up alerts for high data ingestion

## 🔐 Security Considerations

### Data Privacy
- Application Insights may collect sensitive data
- Review and filter logs before production
- Consider data residency requirements
- Implement proper access controls

### Access Control
- Use Azure RBAC for Application Insights access
- Limit access to necessary team members
- Enable audit logging for access tracking

## 📞 Support

### Getting Help
1. Check Azure Application Insights documentation
2. Review Azure Monitor troubleshooting guides
3. Contact Azure support for billing/technical issues
4. Check Food Xchange logs for application-specific issues

### Useful Links
- [Azure Application Insights Documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [OpenCensus Azure Exporter](https://opencensus.io/exporters/supported-exporters/python/azure-monitor/)
- [FastAPI Monitoring Best Practices](https://fastapi.tiangolo.com/tutorial/middleware/)

---

**Note**: This monitoring setup is designed for production use. For development environments, you may want to disable or reduce sampling to minimize costs. 