# Docker Quick Start Guide for FoodXchange

## Prerequisites
- Docker Desktop installed
- Git installed
- Azure credentials in `.env` file

## Quick Start (Development)

### 1. Clone and Setup
```bash
git clone <your-repo>
cd FoodXchange
cp .env.example .env
# Edit .env with your Azure credentials
```

### 2. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Access Application
- Application: http://localhost:8003
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Basic Docker Commands

### Start/Stop Services
```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### Access Container Shell
```bash
# Web application
docker-compose exec web bash

# PostgreSQL
docker-compose exec postgres psql -U postgres -d foodxchange
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up --build

# Force rebuild
docker-compose build --no-cache
```

## Production Deployment

### 1. Create Production Environment File
```bash
cp .env .env.prod
# Edit .env.prod with production credentials
```

### 2. Deploy Production Stack
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Scale Web Service
```bash
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8003
netstat -ano | findstr :8003  # Windows
lsof -i :8003                  # Mac/Linux

# Use different port
# Edit docker-compose.yml: ports: - "8004:8000"
```

### Permission Issues
```bash
# Reset permissions
docker-compose exec web chown -R appuser:appuser /app
```

### Database Connection Issues
```bash
# Check PostgreSQL is healthy
docker-compose ps
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up --build
```

### Azure Connection Issues
```bash
# Test Azure connections
docker-compose exec web python quick_health_check.py
docker-compose exec web python validate_endpoints.py
```

## Environment Variables
Required in `.env`:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_COMMUNICATION_CONNECTION_STRING`
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`

## Development Tips

### Live Code Reloading
Code changes are automatically reflected without rebuilding (development mode only).

### Database Migrations
```bash
# Run migrations
docker-compose exec web alembic upgrade head

# Create new migration
docker-compose exec web alembic revision --autogenerate -m "Description"
```

### Testing
```bash
# Run tests in container
docker-compose exec web pytest

# Run specific test
docker-compose exec web pytest tests/test_azure_services.py
```

## Next Steps
1. Customize `nginx/nginx.conf` for your domain
2. Set up SSL certificates for HTTPS
3. Configure backup schedule in production
4. Set up monitoring with Prometheus/Grafana
5. Implement CI/CD pipeline with Docker