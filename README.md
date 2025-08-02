# FoodXchange - AI-Powered B2B Food Sourcing Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Azure](https://img.shields.io/badge/Azure-Cloud-0078d4.svg)](https://azure.microsoft.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-316192.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-dc382d.svg)](https://redis.io)

FoodXchange is a comprehensive B2B food sourcing platform that leverages AI technology to streamline product analysis, sourcing workflows, and supplier-buyer interactions in the food industry.

## 🚀 Features

### Core Platform
- **AI-Powered Product Analysis** - GPT-4 Vision integration for product specification extraction
- **B2B Sourcing Workflows** - 5-stage sourcing lifecycle management
- **Supplier & Buyer Management** - Comprehensive business relationship management
- **Multi-language Support** - Hebrew and English with Azure Translator integration
- **Document Intelligence** - Automated contract and document processing

### Business Intelligence
- **Project Lifecycle Tracking** - From initiation to completion with stage-based workflows
- **Budget & Cost Management** - Financial tracking and approval workflows
- **Performance Analytics** - Real-time dashboards and reporting
- **Compliance Management** - Kosher, organic, and dietary requirement tracking

### Security & Performance
- **Enterprise Security** - JWT authentication, rate limiting, and CSRF protection
- **Azure Integration** - Cloud-native architecture with managed services
- **Real-time Caching** - Redis-based performance optimization
- **Scalable Architecture** - Microservices-ready modular design

## 🏗️ Architecture

### Technology Stack
```
Frontend:    Jinja2 Templates + Bootstrap 5 + GSAP
Backend:     FastAPI + SQLAlchemy + PostgreSQL
Caching:     Redis with fallback to in-memory
AI/ML:       Azure OpenAI GPT-4 + Computer Vision
Cloud:       Microsoft Azure (PostgreSQL, AI Services)
Container:   Docker + Docker Compose
```

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │────│   FastAPI App   │────│  PostgreSQL DB  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │                   │
            ┌───────────────┐    ┌─────────────┐
            │  Redis Cache  │    │ Azure AI    │
            └───────────────┘    └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Azure account (for AI services)
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd FoodXchange
```

### 2. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
# Required: DATABASE_URL, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY
```

### 3. Start Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Start development server
python start_clean.bat
```

### 4. Access Application
- **Web Interface**: http://localhost:9000
- **API Documentation**: http://localhost:9000/docs
- **Health Check**: http://localhost:9000/health

### 5. Development Login
```
Email: admin@fdx.trading
Password: FDX2030!
```

## 📁 Project Structure

```
FoodXchange/
├── foodxchange/                 # Main application package
│   ├── main.py                 # FastAPI application entry
│   ├── config/                 # Configuration modules
│   │   ├── settings.py         # Application settings
│   │   └── dev_auth.py         # Development authentication
│   ├── core/                   # Core business logic
│   │   ├── auth.py             # Authentication middleware
│   │   ├── security.py         # Security utilities
│   │   └── exceptions.py       # Custom exceptions
│   ├── models/                 # Database models
│   │   ├── user.py             # User model
│   │   ├── project_enhanced.py # Project management
│   │   ├── buyer.py            # Buyer management
│   │   └── supplier.py         # Supplier management
│   ├── routes/                 # API route handlers
│   │   ├── ai_import_routes_fastapi.py
│   │   ├── demo_routes.py
│   │   └── footer_routes.py
│   ├── services/               # Business services
│   │   ├── ai_service.py       # AI integration
│   │   ├── email_service.py    # Email notifications
│   │   └── error_handling/     # Error management
│   ├── middleware/             # Request middleware
│   │   └── rate_limiting.py    # Rate limiting
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html           # Base template
│   │   ├── components/         # Reusable components
│   │   └── pages/              # Page templates
│   └── static/                 # Static assets
│       ├── css/                # Stylesheets
│       ├── js/                 # JavaScript modules
│       └── brand/              # Fonts and logos
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
├── env.example                 # Environment template
└── start_clean.bat            # Development server script
```

## 🔧 Configuration

### Environment Variables

#### Core Configuration
```bash
# Environment
ENVIRONMENT=development          # development|production
DEBUG=true                      # Enable debug mode

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

#### Azure AI Services
```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-vision-preview

# Azure Computer Vision
AZURE_COMPUTER_VISION_ENDPOINT=https://your-vision.cognitiveservices.azure.com/
AZURE_COMPUTER_VISION_KEY=your-key

# Azure Translator
AZURE_TRANSLATOR_KEY=your-translator-key
AZURE_TRANSLATOR_REGION=your-region
```

#### Development Authentication
```bash
# Development Users (only when ENVIRONMENT=development)
DEV_ADMIN_EMAIL=admin@fdx.trading
DEV_ADMIN_PASSWORD=FDX2030!
DEV_USER_EMAIL=user@fdx.trading
DEV_USER_PASSWORD=user123
```

## 🔐 Security

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access**: Admin, operator, and user roles
- **Rate Limiting**: Protection against brute force attacks
- **Password Security**: bcrypt hashing with salt

### Security Headers
- CORS policy with specific allowed origins
- HTTPOnly cookies with SameSite protection
- Content Security Policy (CSP)
- X-Frame-Options and security headers

### Development vs Production
- Environment-based security configuration
- Secure cookie settings based on deployment
- Debug information only in development

## 📊 API Documentation

### Authentication Endpoints
```http
POST /auth/login          # User authentication
POST /auth/logout         # Session termination  
POST /auth/signup         # User registration
```

### Core Application
```http
GET  /                    # Landing page
GET  /dashboard           # Main dashboard (authenticated)
GET  /health              # Health check
GET  /profile             # User profile management
```

### Business Features
```http
GET  /product-analysis/   # AI product analysis
GET  /projects           # Project management
GET  /suppliers          # Supplier management
GET  /buyers             # Buyer management (admin)
```

### AI & Data Processing
```http
POST /ai-import          # AI-enhanced data import
POST /analyze-product    # Product image analysis
GET  /azure-testing      # Azure service testing
```

## 🧪 Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=foodxchange

# Run specific test file
python -m pytest tests/test_auth.py
```

### Development Server
```bash
# Start with auto-reload
python start_clean.bat

# Or manually
python -m uvicorn foodxchange.main:app --reload --port 9000
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Azure Deployment
```bash
# Set production environment
export ENVIRONMENT=production

# Configure Azure PostgreSQL
# Set up Azure AI services
# Deploy using Azure Container Instances or App Service
```

### Production Checklist
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure strong JWT secret key
- [ ] Enable HTTPS with valid certificates
- [ ] Set up Azure PostgreSQL with SSL
- [ ] Configure production Redis instance
- [ ] Review all environment variables
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies
- [ ] Perform security audit

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Add tests for new features
- Update documentation

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

### Getting Help
- Check the [API Documentation](http://localhost:9000/docs)
- Review application logs for error details
- Use the built-in health check endpoint

### Common Issues
1. **Database Connection**: Verify PostgreSQL is running and credentials are correct
2. **Azure AI Services**: Check API keys and endpoint configurations
3. **Authentication**: Ensure JWT secret key is set and valid
4. **Rate Limiting**: Clear Redis cache if hitting rate limits

### Development Support
```bash
# Clear rate limits
python -c "import redis; r=redis.Redis(); r.flushdb()"

# Test database connection
python -c "from foodxchange.database import engine; print(engine.execute('SELECT 1').scalar())"

# Verify environment
python test_login_clean.py
```

---

**FoodXchange** - Revolutionizing B2B food sourcing with AI-powered intelligence.