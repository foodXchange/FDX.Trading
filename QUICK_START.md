# FoodXchange Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Docker Desktop installed
- Git installed
- GitHub account
- Azure OpenAI API key

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/foodxchange.git
cd foodxchange

# Create environment files
fx setup env

# Edit development environment
notepad .env.development
```

### 2. Update .env.development

```env
# Add your Azure OpenAI credentials
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
```

### 3. Start Development

```bash
# Start all services
fx start

# Open in browser
start http://localhost:8003
```

## 📁 Project Structure

```
foodxchange/
├── .github/workflows/    # CI/CD pipelines
├── foodxchange/         # Application code
├── scripts/            # Deployment scripts
├── nginx/             # Nginx configurations
├── docker-compose.*.yml # Environment configs
├── fx.bat             # Management script
└── .env.*            # Environment files
```

## 🔧 Common Commands

### Development
```bash
fx start              # Start development
fx stop               # Stop services
fx logs               # View logs
fx shell              # Enter container
fx test               # Run tests
```

### Database
```bash
fx db connect         # PostgreSQL shell
fx db backup          # Create backup
fx db migrate         # Run migrations
```

### Deployment
```bash
fx deploy staging     # Deploy to staging
fx deploy production  # Show production deploy steps
```

## 🌍 Environments

| Environment | Purpose | URL | Auto-Deploy |
|------------|---------|-----|-------------|
| Development | Local work | http://localhost:8003 | No |
| Staging | Testing | https://staging.foodxchange.com | Yes |
| Production | Live users | https://foodxchange.com | Manual |

## 🔐 Security Setup

### GitHub Secrets Required

1. Go to: Settings → Secrets → Actions
2. Add these secrets:

```
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_KEY
STAGING_SSH_KEY
STAGING_HOST
STAGING_USER
PRODUCTION_SSH_KEY
PRODUCTION_HOSTS
PRODUCTION_USER
```

## 📊 Monitoring

### Health Checks
```bash
# Development
curl http://localhost:8003/health

# Staging
curl https://staging.foodxchange.com/health

# Production
curl https://foodxchange.com/health
```

### View Logs
```bash
fx logs              # All logs
fx logs web          # Web server only
fx monitor logs      # Tail logs
```

## 🚨 Troubleshooting

### Service Won't Start
```bash
fx clean all         # Clean everything
fx start             # Try again
```

### Database Issues
```bash
fx db status         # Check database
fx restart           # Restart all services
```

### Port Conflicts
```bash
# Windows: Find process using port
netstat -ano | findstr :8003
taskkill /PID <PID> /F
```

## 📚 Next Steps

1. Read [Git Workflow](./docs/GIT_WORKFLOW.md)
2. Review [Deployment Guide](./DEPLOYMENT.md)
3. Set up staging server
4. Configure GitHub Actions
5. Plan production deployment

## 💡 Pro Tips

1. **Always work in feature branches**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Test before deploying**
   ```bash
   fx test
   fx lint
   ```

3. **Use the fx script**
   - It handles environment switching
   - Prevents accidental production changes
   - Provides consistent commands

4. **Monitor your deployments**
   - Check GitHub Actions
   - Watch staging logs
   - Verify health endpoints

## 🆘 Getting Help

- GitHub Issues: Report bugs
- Documentation: Check `/docs`
- Logs: Always check logs first
- Team: Ask in Slack/Teams

---

Happy coding! 🎉