# Azure Services Details - Poland Central Infrastructure

## 🏗️ Current Architecture (Poland Central)

### Resource Groups

#### fdx-prod-rg (Poland Central)
- **fdx-poland-vm** (Virtual Machine)
  - Size: Standard_B2s (2 vCPUs, 4 GB RAM)
  - OS: Ubuntu 22.04 LTS
  - IP: 74.248.141.31
  - Location: Poland Central
- **Network Security Group**
- **Public IP Address**

#### fdx-data-rg (Poland Central)
- **fdx-poland-db** (PostgreSQL Database)
  - Server: fdx-poland-db.postgres.database.azure.com
  - Database: foodxchange
  - Size: ~2GB current database size
  - Location: Poland Central

#### fdx-trading-rg (Canada Central)
- **SSL Certificate** for fdx.trading domain

### 1. Azure Database for PostgreSQL

**Service Details:**
- **Resource**: fdx-poland-db
- **Region**: Poland Central
- **Server**: fdx-poland-db.postgres.database.azure.com
- **Database**: foodxchange
- **Connection String**: `postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require`

**Performance:**
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Data Size**: ~2GB
- **Suppliers**: 17,771+ records

**Monthly Cost**: ~$24.82

### 2. Azure OpenAI Service

**Service Details:**
- **Resource**: Cognitive Services
- **Region**: East US
- **Endpoint**: `https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/`
- **Model Deployment**: gpt-4o-mini

**Usage Patterns:**
- Email generation: ~500-1000 requests/day
- Supplier matching: ~100-200 requests/day
- Average tokens per request: 200-500
- Caching reduces calls by 60-80%

**Cost Structure:**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Estimated monthly: $10-50

**Optimizations Applied:**
- Response caching (1-hour TTL)
- Token limits (500 max)
- Batch processing
- Fallback templates

### 3. Virtual Machine (fdx-poland-vm)

**Current Setup**: Poland Central
- **Size**: Standard_B2s (2 vCPUs, 4 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **IP**: 74.248.141.31
- **Location**: Poland Central
- **Resource Group**: fdx-prod-rg

**Services Running:**
- FastAPI Application (port 8000)
- Nginx Web Server (port 80)
- Email CRM System (port 8003)
- Grafana Monitoring (port 3000)
- Netdata Monitoring (port 19999)

**Monthly Cost**: ~$32.18

### 4. Monitoring Services

**Configured Services:**
- Application Insights (pending setup)
- Log Analytics Workspace (pending setup)
- Custom Metrics API

**Target Configuration:**
- Data ingestion: ~45GB/month
- Metric time series: 500-1000
- Log retention: 30 days
- **Target Cost**: $100/month (to earn credits)

## Service Integration Map

```
┌─────────────────────────────────────────────────────────┐
│                    FDX.trading App                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │   FastAPI   │  │ Email Service │  │ Cost Tracker  │ │
│  │   Routes    │  │   (Cached)    │  │  & Alerts     │ │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘ │
│         │                 │                   │         │
└─────────┼─────────────────┼─────────────────┼─────────┘
          │                 │                   │
          ▼                 ▼                   ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  PostgreSQL DB  │ │ Azure OpenAI │ │ Azure Monitor   │
│  (Poland)       │ │ (Cognitive)  │ │ (App Insights)  │
└─────────────────┘ └──────────────┘ └─────────────────┘
```

## Resource Naming Convention

```
Resource Type       | Naming Pattern           | Example
--------------------|-------------------------|---------------------------
Resource Group      | fdx-[env]-rg           | fdx-prod-rg
PostgreSQL Server   | fdx-poland-db          | fdx-poland-db
Virtual Machine     | fdx-poland-vm          | fdx-poland-vm
Cognitive Services  | fdx-ai-[env]           | fdx-ai-prod
App Service         | fdx-app-[env]          | fdx-app-prod
Storage Account     | fdxstorage[env]        | fdxstorageprod
```

## Security Configuration

### Network Security
- PostgreSQL: Public access with IP allowlist
- Firewall rules configured for development
- SSL/TLS required for all connections
- No VNet integration (cost optimization)

### Authentication
- PostgreSQL: Password authentication
- OpenAI: API key authentication
- VM: SSH key-based authentication
- Future: Managed Identity for production

## Performance & Cost Optimization

### Current Performance
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Total Monthly Cost**: $57 (saving $3/month vs US East)
- **Database Performance**: Optimized queries and indexing
- **Application Response**: <200ms average

### Cost Breakdown
- **PostgreSQL Database**: $24.82/month
- **Virtual Machine**: $32.18/month
- **Azure OpenAI**: $10-50/month (variable)
- **Total**: $67-107/month

### Optimizations Applied
1. **Database**: Query optimization, indexing
2. **Application**: Response caching, static file serving
3. **Network**: Poland Central location for European traffic
4. **Monitoring**: Efficient logging and metrics collection

## Migration History

### 2025-01-XX: Poland Central Migration
- ✅ Migrated from US East to Poland Central
- ✅ Created new resource groups: fdx-prod-rg, fdx-data-rg
- ✅ Deployed new VM: fdx-poland-vm (74.248.141.31)
- ✅ Created new database: fdx-poland-db
- ✅ Migrated 17,771 suppliers with all data intact
- ✅ Updated all connection strings and configurations
- ✅ Performance improvement: 200ms → 30ms latency

### Benefits Achieved
- **Performance**: 6x faster response times
- **Cost**: $3/month savings
- **Reliability**: Better network connectivity
- **Scalability**: Optimized for European market

## Future Improvements

### Planned Optimizations
1. **Load Balancing**: Add multiple VM instances
2. **CDN**: CloudFlare integration for static assets
3. **Auto-scaling**: Based on traffic patterns
4. **Enhanced Monitoring**: Application Insights setup
5. **Backup Strategy**: Automated daily backups

### Cost Management
- Monitor Azure OpenAI usage closely
- Set up spending alerts at 50%, 80%, 100%
- Regular cost optimization reviews
- Consider reserved instances for predictable workloads