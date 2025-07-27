# FoodXchange System Monitoring Guide

## Overview

This guide covers the comprehensive monitoring system for FoodXchange, including real-time system health checks, Azure service monitoring, and automated alerting.

## 🚀 Quick Start

### Option 1: Interactive Menu (Recommended)
```bash
# Run the interactive monitoring menu
run-system-monitor.bat
```

### Option 2: Direct Script Execution
```bash
# Quick 30-second check
powershell -ExecutionPolicy Bypass -File "quick-monitor.ps1" -Interval 10 -Duration 30

# Standard 5-minute monitoring
powershell -ExecutionPolicy Bypass -File "quick-monitor.ps1" -Interval 30 -Duration 300

# Comprehensive Python monitoring
python system_monitor.py
```

## 📊 Monitoring Scripts

### 1. `system_monitor.py` - Comprehensive Python Monitor

**Features:**
- Complete system health assessment
- Database connectivity testing
- Azure services status checking
- Application endpoint monitoring
- Performance metrics collection
- Detailed JSON reports
- Alert generation

**Usage:**
```bash
# Basic monitoring
python system_monitor.py

# Save report to specific file
python -c "from system_monitor import SystemMonitor; monitor = SystemMonitor(); monitor.generate_report(); monitor.save_report('my_report.json')"
```

**Output:**
- Console summary with color-coded status
- Detailed JSON report file
- System log entries
- Exit codes: 0 (healthy), 1 (critical), 2 (warning)

### 2. `continuous_monitor.py` - Background Monitoring

**Features:**
- Continuous monitoring with configurable intervals
- Email and webhook alerts
- Automatic report archiving
- Failure threshold management
- Alert cooldown to prevent spam

**Usage:**
```bash
# Start continuous monitoring (5-minute intervals)
python continuous_monitor.py --interval 5

# Custom alert threshold (3 consecutive failures)
python continuous_monitor.py --interval 5 --threshold 3

# Run as background daemon
python continuous_monitor.py --daemon
```

**Configuration:**
Set these environment variables for alerts:
```env
# Email Alerts
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAILS=admin@foodxchange.com,ops@foodxchange.com

# Webhook Alerts
WEBHOOK_ALERTS_ENABLED=true
WEBHOOK_URL=https://your-webhook-url.com/endpoint
WEBHOOK_SECRET=your-webhook-secret
```

### 3. `quick-monitor.ps1` - PowerShell Quick Monitor

**Features:**
- Real-time system metrics
- Database connection testing
- Azure service status
- Application health checks
- Color-coded status display
- Configurable intervals

**Usage:**
```powershell
# Quick 30-second check
.\quick-monitor.ps1 -Interval 10 -Duration 30

# Extended monitoring
.\quick-monitor.ps1 -Interval 60 -Duration 900
```

## 🔧 Azure Deployment Monitoring

### Fixing GitHub Actions Credential Issues

If you encounter "No credentials found" errors in GitHub Actions:

#### Option 1: Automated Setup
```bash
# Run the automated setup script
.\setup-azure-credentials.ps1
```

#### Option 2: Manual Setup

1. **Create Azure Service Principal:**
   ```bash
   az ad sp create-for-rbac --name "foodxchange-github-actions" --role Contributor --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID"
   ```

2. **Add GitHub Secrets:**
   Go to your GitHub repository → Settings → Secrets and variables → Actions
   Add these secrets:
   - `AZURE_CLIENT_ID` = Application (client) ID
   - `AZURE_TENANT_ID` = Directory (tenant) ID  
   - `AZURE_SUBSCRIPTION_ID` = Subscription ID

3. **Update Workflow File:**
   The workflow file has been updated to use the correct secret names.

## 📈 Monitoring Metrics

### System Metrics
- **CPU Usage:** Real-time processor utilization
- **Memory Usage:** RAM consumption percentage
- **Disk Usage:** Storage space utilization
- **Network Status:** Active network interfaces
- **Process Count:** Number of running processes
- **System Uptime:** Time since last reboot

### Database Metrics
- **Connection Status:** Database connectivity
- **Response Time:** Query execution time
- **Server Time:** Database server timestamp
- **Error Details:** Connection failure reasons

### Azure Services
- **OpenAI Service:** API endpoint health
- **Storage Service:** Blob storage connectivity
- **PostgreSQL:** Azure database status

### Application Health
- **Health Endpoint:** `/health` endpoint status
- **API Status:** `/api/v1/status` endpoint
- **Response Times:** HTTP request latency
- **Error Rates:** Failed request tracking

## 🚨 Alert System

### Alert Types
- **SYSTEM_ERROR:** System information collection failures
- **DATABASE_ERROR:** Database connection issues
- **AZURE_OPENAI_ERROR:** Azure OpenAI service problems
- **AZURE_STORAGE_ERROR:** Azure Storage connectivity issues
- **AZURE_POSTGRESQL_ERROR:** Azure PostgreSQL problems
- **APPLICATION_ERROR:** Application endpoint failures
- **PERFORMANCE_WARNING:** High resource usage alerts

### Alert Severity
- **High:** Critical system failures requiring immediate attention
- **Medium:** Performance warnings and degraded service states

### Alert Channels
- **Email:** SMTP-based alert notifications
- **Webhook:** HTTP POST to external systems
- **Console:** Real-time console output
- **Logs:** Persistent log file entries

## 📁 File Structure

```
FoodXchange/
├── system_monitor.py              # Comprehensive Python monitor
├── continuous_monitor.py          # Background monitoring service
├── quick-monitor.ps1             # PowerShell quick monitor
├── run-system-monitor.bat        # Interactive monitoring menu
├── setup-azure-credentials.ps1   # Azure credentials setup
├── monitoring_reports/           # Archived monitoring reports
│   ├── monitoring_report_20241224_143022.json
│   └── ...
├── logs/                         # Monitoring logs
│   ├── system_monitor.log
│   ├── continuous_monitor.log
│   └── ...
└── docs/
    └── SYSTEM_MONITORING_GUIDE.md  # This file
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Failures
```bash
# Check environment variables
echo $DATABASE_URL

# Test connection manually
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); print('Connected')"
```

#### 2. Azure Service Issues
```bash
# Check Azure credentials
az account show

# Test Azure services
python -c "import os; print('OpenAI:', bool(os.getenv('AZURE_OPENAI_ENDPOINT')))"
```

#### 3. Application Health Issues
```bash
# Check if application is running
curl http://localhost:8000/health

# Check application logs
tail -f app.log
```

#### 4. PowerShell Execution Policy
```powershell
# Fix execution policy issues
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Performance Optimization

#### 1. Reduce Monitoring Frequency
```bash
# For high-traffic systems, increase intervals
python continuous_monitor.py --interval 10  # 10-minute intervals
```

#### 2. Limit Report Retention
```python
# In continuous_monitor.py, modify cleanup_old_reports
monitor.cleanup_old_reports(days_to_keep=3)  # Keep only 3 days
```

#### 3. Selective Monitoring
```python
# Modify system_monitor.py to skip certain checks
# Comment out specific check methods in generate_report()
```

## 🛠️ Customization

### Adding Custom Metrics

1. **Extend SystemMonitor Class:**
   ```python
   def check_custom_metric(self):
       # Your custom monitoring logic
       return {'status': 'healthy', 'value': 42}
   ```

2. **Add to Report Generation:**
   ```python
   def generate_report(self):
       # ... existing code ...
       self.results['custom_metrics'] = self.check_custom_metric()
   ```

### Custom Alert Rules

1. **Modify Alert Thresholds:**
   ```python
   # In system_monitor.py
   if perf_info['cpu_usage'] > 90:  # Change from 80 to 90
       self.add_alert("PERFORMANCE_WARNING", f"High CPU usage: {perf_info['cpu_usage']}%")
   ```

2. **Add Custom Alert Types:**
   ```python
   def add_custom_alert(self, message):
       self.add_alert("CUSTOM_ALERT", message)
   ```

## 📊 Reporting

### Report Formats

#### JSON Reports
```json
{
  "timestamp": "2024-12-24T14:30:22",
  "summary": {
    "overall_status": "healthy",
    "total_alerts": 0,
    "critical_alerts": 0
  },
  "system_info": { ... },
  "database": { ... },
  "azure_services": { ... },
  "application": { ... },
  "performance": { ... },
  "alerts": []
}
```

#### Console Output
```
============================================================
FOODXCHANGE SYSTEM MONITORING REPORT
============================================================
Timestamp: 2024-12-24T14:30:22
Overall Status: HEALTHY
Alerts: 0 (Critical: 0)

--- SYSTEM INFO ---
Platform: Windows-10-10.0.19045-SP0
CPU Usage: 15.2%
Memory Usage: 45.8%

--- DATABASE ---
Status: healthy
Connection Time: 45.2ms

--- AZURE SERVICES ---
OpenAI: healthy
Storage: configured
PostgreSQL: healthy

--- APPLICATION ---
Status: healthy
  health: healthy
  api: healthy
============================================================
```

## 🔄 Integration

### CI/CD Integration

Add monitoring to your deployment pipeline:

```yaml
# .github/workflows/monitor.yml
name: System Monitoring
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run System Monitor
        run: python system_monitor.py
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: monitoring-report
          path: monitoring_report_*.json
```

### External Monitoring Integration

#### Prometheus Metrics
```python
# Add Prometheus metrics export
from prometheus_client import Counter, Gauge, generate_latest

cpu_gauge = Gauge('system_cpu_usage', 'CPU usage percentage')
memory_gauge = Gauge('system_memory_usage', 'Memory usage percentage')

# Update metrics in monitoring
cpu_gauge.set(perf_info['cpu_usage'])
memory_gauge.set(perf_info['memory_usage'])
```

#### Grafana Dashboard
Create dashboards using the JSON reports or Prometheus metrics for visualization.

## 📚 Best Practices

### 1. Monitoring Frequency
- **Development:** Every 5-10 minutes
- **Staging:** Every 2-5 minutes  
- **Production:** Every 1-2 minutes

### 2. Alert Management
- Set appropriate thresholds to avoid alert fatigue
- Use alert cooldowns to prevent spam
- Escalate critical alerts immediately

### 3. Log Management
- Rotate log files regularly
- Archive old monitoring reports
- Monitor log file sizes

### 4. Resource Usage
- Monitor the monitoring system itself
- Use efficient data collection methods
- Clean up old data periodically

## 🆘 Support

### Getting Help

1. **Check Logs:** Review monitoring logs for detailed error information
2. **Run Diagnostics:** Use the quick monitor for immediate status
3. **Review Configuration:** Verify environment variables and settings
4. **Check Dependencies:** Ensure all required packages are installed

### Common Commands

```bash
# Install monitoring dependencies
pip install psutil requests azure-storage-blob

# Check monitoring status
python system_monitor.py

# View recent logs
tail -f system_monitor.log

# Test specific components
python -c "from system_monitor import SystemMonitor; m = SystemMonitor(); print(m.check_database_connection())"
```

---

**Last Updated:** December 24, 2024  
**Version:** 1.0.0  
**Maintainer:** FoodXchange Development Team 