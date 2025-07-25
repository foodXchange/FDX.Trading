# FoodXchange Configuration Guide

## Overview

This guide covers all configuration options for the FoodXchange platform, including environment variables, database settings, and application configuration.

## Environment Variables

### Required Variables

#### Database Configuration
```env
# PostgreSQL Database URL
DATABASE_URL=postgresql://username:password@host:port/database_name

# Example for local development
DATABASE_URL=postgresql://foodxchange_user:password123@localhost:5432/foodxchange_db

# Example for Azure Database for PostgreSQL
DATABASE_URL=postgresql://foodxchange_admin@foodxchange-db.postgres.database.azure.com:5432/foodxchange_db
```

#### Security Configuration
```env
# Secret key for JWT token generation (generate a secure random key)
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random

# JWT token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Algorithm for JWT tokens
ALGORITHM=HS256
```

### Optional Variables

#### Email Configuration
```env
# SMTP Server Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Email sender information
EMAILS_FROM_EMAIL=noreply@foodxchange.com
EMAILS_FROM_NAME=FoodXchange Platform

# Enable/disable email notifications
EMAILS_ENABLED=true
```

#### OpenAI Configuration (for AI features)
```env
# OpenAI API Key for AI-powered features
OPENAI_API_KEY=sk-your-openai-api-key-here

# OpenAI model to use
OPENAI_MODEL=gpt-3.5-turbo

# Maximum tokens for AI responses
OPENAI_MAX_TOKENS=1000
```

#### Azure Storage Configuration
```env
# Azure Storage Connection String
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net

# Azure Storage Container for file uploads
AZURE_CONTAINER_NAME=foodxchange-files

# Enable/disable Azure Storage
AZURE_STORAGE_ENABLED=false
```

#### Redis Configuration (for caching)
```env
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# Redis password (if required)
REDIS_PASSWORD=your-redis-password

# Enable/disable Redis caching
REDIS_ENABLED=false
```

#### Application Configuration
```env
# Application name and version
PROJECT_NAME=FoodXchange
VERSION=1.0.0

# API version prefix
API_V1_STR=/api/v1

# CORS origins (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://your-domain.com

# Debug mode (set to false in production)
DEBUG=false

# Log level
LOG_LEVEL=INFO
```

#### First Superuser Configuration
```env
# First superuser credentials (for initial setup)
FIRST_SUPERUSER_EMAIL=admin@foodxchange.com
FIRST_SUPERUSER_PASSWORD=changeme123
FIRST_SUPERUSER_FULL_NAME=System Administrator
```

## Configuration Files

### .env File

Create a `.env` file in the root directory with your configuration:

```env
# Database
DATABASE_URL=postgresql://foodxchange_user:password123@localhost:5432/foodxchange_db

# Security
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@foodxchange.com
EMAILS_FROM_NAME=FoodXchange Platform
EMAILS_ENABLED=true

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=foodxchange-files
AZURE_STORAGE_ENABLED=false

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password
REDIS_ENABLED=false

# Application
PROJECT_NAME=FoodXchange
VERSION=1.0.0
API_V1_STR=/api/v1
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://your-domain.com
DEBUG=false
LOG_LEVEL=INFO

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@foodxchange.com
FIRST_SUPERUSER_PASSWORD=changeme123
FIRST_SUPERUSER_FULL_NAME=System Administrator
```

### Configuration Validation

The application validates all required environment variables on startup. Missing required variables will cause the application to fail to start.

## Environment-Specific Configurations

### Development Environment

```env
# Development settings
DEBUG=true
LOG_LEVEL=DEBUG
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EMAILS_ENABLED=false
REDIS_ENABLED=false
AZURE_STORAGE_ENABLED=false
```

### Staging Environment

```env
# Staging settings
DEBUG=false
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS=https://staging.foodxchange.com
EMAILS_ENABLED=true
REDIS_ENABLED=true
AZURE_STORAGE_ENABLED=true
```

### Production Environment

```env
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
BACKEND_CORS_ORIGINS=https://foodxchange.com,https://www.foodxchange.com
EMAILS_ENABLED=true
REDIS_ENABLED=true
AZURE_STORAGE_ENABLED=true
```

## Database Configuration

### PostgreSQL Settings

#### Connection Pooling
```env
# Database connection pool settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

#### SSL Configuration
```env
# Enable SSL for database connections (recommended for production)
DATABASE_SSL_MODE=require
DATABASE_SSL_CERT=
DATABASE_SSL_KEY=
DATABASE_SSL_CA=
```

### Database URL Format

The `DATABASE_URL` follows this format:
```
postgresql://username:password@host:port/database_name?sslmode=require
```

#### Examples

**Local Development:**
```
postgresql://foodxchange_user:password123@localhost:5432/foodxchange_db
```

**Azure Database for PostgreSQL:**
```
postgresql://foodxchange_admin@foodxchange-db.postgres.database.azure.com:5432/foodxchange_db?sslmode=require
```

**Heroku PostgreSQL:**
```
postgresql://username:password@host:port/database_name?sslmode=require
```

## Security Configuration

### JWT Token Settings

```env
# JWT Secret Key (generate a secure random key)
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random

# Token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES=30

# JWT algorithm
ALGORITHM=HS256
```

### CORS Configuration

```env
# Allowed origins (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://your-domain.com
```

### Password Security

```env
# Password hashing rounds (higher = more secure, slower)
PASSWORD_HASH_ROUNDS=12

# Minimum password length
MIN_PASSWORD_LENGTH=8
```

## Email Configuration

### SMTP Settings

```env
# SMTP Server
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Authentication
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Sender information
EMAILS_FROM_EMAIL=noreply@foodxchange.com
EMAILS_FROM_NAME=FoodXchange Platform

# Enable/disable emails
EMAILS_ENABLED=true
```

### Email Templates

Email templates are stored in the `app/templates/emails/` directory and use Jinja2 templating.

## AI Configuration

### OpenAI Settings

```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Model to use
OPENAI_MODEL=gpt-3.5-turbo

# Maximum tokens for responses
OPENAI_MAX_TOKENS=1000

# Temperature (creativity level)
OPENAI_TEMPERATURE=0.7
```

## Azure Configuration

### Storage Settings

```env
# Azure Storage Connection String
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net

# Container name for file uploads
AZURE_CONTAINER_NAME=foodxchange-files

# Enable/disable Azure Storage
AZURE_STORAGE_ENABLED=false
```

## Redis Configuration

### Caching Settings

```env
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# Redis password (if required)
REDIS_PASSWORD=your-redis-password

# Enable/disable Redis
REDIS_ENABLED=false

# Cache expiration time (seconds)
REDIS_CACHE_EXPIRY=300
```

## Logging Configuration

### Log Levels

```env
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log format
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Log file path (optional)
LOG_FILE=logs/foodxchange.log
```

## Application Settings

### General Settings

```env
# Application name
PROJECT_NAME=FoodXchange

# Application version
VERSION=1.0.0

# API version prefix
API_V1_STR=/api/v1

# Debug mode
DEBUG=false

# Host and port for development server
HOST=0.0.0.0
PORT=8000
```

## Configuration Validation

### Required Variables Check

The application validates these required variables on startup:

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALGORITHM`

### Optional Variables

These variables have default values if not set:

- `DEBUG` (default: `false`)
- `LOG_LEVEL` (default: `INFO`)
- `EMAILS_ENABLED` (default: `false`)
- `REDIS_ENABLED` (default: `false`)
- `AZURE_STORAGE_ENABLED` (default: `false`)

## Environment Variable Best Practices

### Security

1. **Never commit sensitive data** to version control
2. **Use strong, random secret keys**
3. **Rotate secrets regularly**
4. **Use environment-specific configurations**

### Organization

1. **Group related variables** together
2. **Use descriptive variable names**
3. **Document all variables**
4. **Provide example values**

### Validation

1. **Validate required variables** on startup
2. **Provide meaningful error messages**
3. **Use type checking** where possible
4. **Test configurations** in different environments

## Troubleshooting Configuration Issues

### Common Issues

1. **Missing Required Variables**
   ```
   Error: Required environment variable 'DATABASE_URL' not set
   Solution: Add DATABASE_URL to your .env file
   ```

2. **Invalid Database URL**
   ```
   Error: Invalid database URL format
   Solution: Check DATABASE_URL format and credentials
   ```

3. **CORS Issues**
   ```
   Error: CORS policy violation
   Solution: Add your domain to BACKEND_CORS_ORIGINS
   ```

4. **Email Configuration**
   ```
   Error: SMTP authentication failed
   Solution: Check SMTP credentials and enable app passwords
   ```

### Debug Mode

Enable debug mode to see detailed error messages:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## Configuration Examples

### Complete Development Configuration

```env
# Database
DATABASE_URL=postgresql://foodxchange_user:password123@localhost:5432/foodxchange_db

# Security
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Application
PROJECT_NAME=FoodXchange
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=true
LOG_LEVEL=DEBUG
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Email (disabled for development)
EMAILS_ENABLED=false

# AI (optional)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Storage (disabled for development)
AZURE_STORAGE_ENABLED=false
REDIS_ENABLED=false

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@foodxchange.com
FIRST_SUPERUSER_PASSWORD=changeme123
FIRST_SUPERUSER_FULL_NAME=System Administrator
```

### Complete Production Configuration

```env
# Database
DATABASE_URL=postgresql://foodxchange_admin@foodxchange-db.postgres.database.azure.com:5432/foodxchange_db?sslmode=require

# Security
SECRET_KEY=your-super-secret-production-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Application
PROJECT_NAME=FoodXchange
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=false
LOG_LEVEL=WARNING
BACKEND_CORS_ORIGINS=https://foodxchange.com,https://www.foodxchange.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@foodxchange.com
EMAILS_FROM_NAME=FoodXchange Platform
EMAILS_ENABLED=true

# AI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=foodxchange-files
AZURE_STORAGE_ENABLED=true

# Redis
REDIS_URL=redis://your-redis-host:6379/0
REDIS_PASSWORD=your-redis-password
REDIS_ENABLED=true
```

## Support

For configuration issues:

- **Email**: config@foodxchange.com
- **Documentation**: [Configuration Guide](CONFIGURATION.md)
- **GitHub Issues**: [Configuration Issues](https://github.com/yourusername/foodxchange/issues) 