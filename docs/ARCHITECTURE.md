# FoodXchange Architecture Documentation

## System Overview

FoodXchange is a cloud-native B2B food sourcing platform built with modern Python technologies and Azure AI services. The architecture emphasizes scalability, security, and AI-powered intelligence for food industry operations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Jinja2 Templates + Bootstrap 5 + GSAP + Custom JavaScript     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    API Gateway Layer                            │
├─────────────────────────────────────────────────────────────────┤
│         FastAPI + CORS + Rate Limiting + Authentication        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                 Application Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Auth      │ │   AI        │ │  Business   │ │   Admin     │ │
│  │  Services   │ │  Services   │ │  Services   │ │  Services   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   Data Layer                                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ PostgreSQL  │ │    Redis    │ │   Azure     │ │   File      │ │
│  │  Database   │ │    Cache    │ │ AI Services │ │   Storage   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend Technologies
- **FastAPI 0.104.1** - Modern async web framework
- **Python 3.11+** - Programming language
- **SQLAlchemy 2.0** - ORM with async support
- **Pydantic** - Data validation and settings
- **uvicorn** - ASGI server

### Database & Caching
- **PostgreSQL 16** - Primary database (Azure managed)
- **Redis 7** - Caching and session storage
- **SQLAlchemy Core/ORM** - Database abstraction
- **Alembic** - Database migrations

### AI/ML Services
- **Azure OpenAI GPT-4** - Product analysis and reasoning
- **Azure Computer Vision** - Image processing
- **Azure Translator** - Multi-language support
- **Azure Document Intelligence** - Document processing
- **Azure Cognitive Search** - Product indexing

### Frontend Technologies
- **Jinja2** - Server-side templating
- **Bootstrap 5.3.0** - UI framework
- **GSAP 3.12** - Animation library
- **Font Awesome 6.4** - Icon library
- **Custom JavaScript** - Interactive features

### Infrastructure
- **Docker** - Containerization
- **Azure Container Registry** - Image storage
- **Azure Container Instances** - Container hosting
- **Azure Storage** - File storage
- **Azure Application Insights** - Monitoring

## Application Architecture

### Layered Architecture Pattern

#### 1. Presentation Layer
```
templates/
├── base.html              # Base template with common elements
├── components/            # Reusable UI components
│   ├── navbar.html        # Navigation component
│   ├── footer.html        # Footer component
│   └── modals/           # Modal dialogs
└── pages/                # Page-specific templates
    ├── dashboard.html     # Main dashboard
    ├── login.html        # Authentication
    └── product_analysis.html
```

#### 2. API Layer
```
routes/
├── auth_routes.py         # Authentication endpoints
├── ai_import_routes.py    # AI-powered data import
├── demo_routes.py         # Demo and showcase
└── footer_routes.py       # Static page routes
```

#### 3. Business Logic Layer
```
services/
├── ai_service.py          # AI integration service
├── email_service.py       # Email notifications
├── error_handling/        # Error management
│   └── error_analyzer.py  # Error analysis
└── auth_service.py        # Authentication business logic
```

#### 4. Data Access Layer
```
models/
├── user.py               # User management
├── project_enhanced.py   # Project lifecycle
├── buyer.py             # Buyer management
├── supplier.py          # Supplier management
└── base.py              # Base model classes
```

### Core Components

#### Authentication System
```python
# JWT-based authentication with role-based access
core/
├── auth.py              # Authentication middleware
├── security.py          # Security utilities (JWT, password hashing)
└── exceptions.py        # Custom authentication exceptions

# Features:
- JWT token authentication
- bcrypt password hashing
- Role-based authorization (Admin, Operator, User)
- Rate limiting protection
- Session management
```

#### AI Integration Service
```python
services/ai_service.py

class AIService:
    def analyze_product_image(image: bytes) -> ProductAnalysis
    def extract_specifications(text: str) -> Dict
    def translate_content(text: str, target_lang: str) -> str
    def process_document(file: bytes) -> DocumentData
```

#### Business Domain Models
```python
# User Management
class User(BaseModel):
    - Personal information (name, email, company)
    - Authentication details (password_hash, role)
    - Profile preferences (timezone, language)
    - Business context (industry, job_title)

# Project Management
class Project(BaseModel):
    - 5-stage sourcing workflow
    - Budget and timeline tracking
    - AI analysis results
    - Document attachments

# Supplier/Buyer Management
class Supplier(BaseModel):
    - Contact and business information
    - Certifications and capabilities
    - Rating and review system
    - Payment terms and conditions
```

## Database Architecture

### Entity Relationship Diagram
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Users    │────▶│  Projects   │◄────│   Buyers    │
│             │     │             │     │             │
│ - id        │     │ - id        │     │ - id        │
│ - email     │     │ - title     │     │ - name      │
│ - role      │     │ - status    │     │ - industry  │
│ - profile   │     │ - budget    │     │ - verified  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   
       │                   │                   
       ▼                   ▼                   
┌─────────────┐     ┌─────────────┐     
│ Notifications│     │ Suppliers   │     
│             │     │             │     
│ - id        │     │ - id        │     
│ - user_id   │     │ - name      │     
│ - type      │     │ - rating    │     
│ - read      │     │ - certs     │     
└─────────────┘     └─────────────┘     
```

### Database Schema

#### Core Tables
```sql
-- Users table with comprehensive profile
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Projects with sourcing workflow
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'INITIATED',
    budget DECIMAL(12,2),
    completion_percentage INTEGER DEFAULT 0,
    ai_analysis_results JSONB,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Suppliers with business details
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    company_size VARCHAR(50),
    certifications TEXT[],
    rating DECIMAL(3,2),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Performance Optimizations
```sql
-- Indexes for query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_suppliers_verified ON suppliers(is_verified);

-- JSONB indexes for AI analysis results
CREATE INDEX idx_projects_ai_analysis ON projects USING GIN(ai_analysis_results);
```

## Security Architecture

### Authentication Flow
```
1. User Login Request
   ├── Rate Limiting Check
   ├── Credential Validation
   ├── Password Verification (bcrypt)
   └── JWT Token Generation

2. Request Authentication
   ├── JWT Token Extraction (HTTPOnly Cookie)
   ├── Token Signature Verification
   ├── Token Expiration Check
   └── User Context Loading

3. Authorization Check
   ├── Role-based Access Control
   ├── Resource Permission Check
   └── Request Processing
```

### Security Layers
```python
# 1. Network Security
- HTTPS/TLS encryption
- CORS policy enforcement
- Rate limiting by IP
- Azure firewall rules

# 2. Application Security
- JWT token authentication
- bcrypt password hashing
- SQL injection prevention (ORM)
- XSS protection (template escaping)
- CSRF token validation

# 3. Data Security
- Database encryption at rest
- Sensitive data masking in logs
- Environment variable secrets
- Azure Key Vault integration
```

### Rate Limiting Strategy
```python
middleware/rate_limiting.py

# Rate limits by endpoint type:
- Login attempts: 5 per 5 minutes per IP
- API calls: 100 per minute per user
- File uploads: 10 per hour per user
- AI analysis: 20 per hour per user

# Implementation:
- Redis-based distributed rate limiting
- Sliding window algorithm
- Progressive penalties for abuse
- Whitelist for trusted IPs
```

## AI Services Architecture

### Azure AI Integration
```python
services/ai_service.py

class AzureAIService:
    # GPT-4 Vision for product analysis
    async def analyze_product_image(self, image_data: bytes) -> ProductAnalysis:
        - Image preprocessing and validation
        - GPT-4 Vision API call with custom prompts
        - Response parsing and validation
        - Results caching for performance

    # Computer Vision for image processing
    async def extract_image_features(self, image: bytes) -> ImageFeatures:
        - Azure Computer Vision API integration
        - Feature extraction (objects, text, brands)
        - Confidence scoring
        - Metadata extraction

    # Document Intelligence for contract processing
    async def process_document(self, document: bytes) -> DocumentData:
        - Document format detection
        - Content extraction and structuring
        - Entity recognition
        - Data validation and normalization
```

### AI Workflow Pipeline
```
1. Input Processing
   ├── File validation and sanitization
   ├── Format detection and conversion
   ├── Size and security checks
   └── Metadata extraction

2. AI Analysis
   ├── Service selection based on content type
   ├── API call with error handling and retries
   ├── Response validation and parsing
   └── Confidence scoring

3. Result Processing
   ├── Data normalization and validation
   ├── Database storage
   ├── Cache update
   └── User notification
```

## Deployment Architecture

### Local Development
```
┌─────────────────┐
│  Development    │
│   Environment   │
├─────────────────┤
│ FastAPI Server  │
│ Port: 9000      │
├─────────────────┤
│ PostgreSQL      │
│ Docker Container│
├─────────────────┤
│ Redis Cache     │
│ Docker Container│
└─────────────────┘
```

### Production Azure Deployment
```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure Cloud                              │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Azure     │ │   Azure     │ │   Azure     │ │   Azure     │ │
│ │   Front     │ │  Container  │ │  Database   │ │    Cache    │ │
│ │   Door      │ │  Instances  │ │     for     │ │     for     │ │
│ │  (CDN/WAF)  │ │   (Apps)    │ │ PostgreSQL  │ │    Redis    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Azure     │ │   Azure     │ │   Azure     │ │   Azure     │ │
│ │   OpenAI    │ │  Computer   │ │  Document   │ │  Storage    │ │
│ │  Service    │ │   Vision    │ │Intelligence │ │  Account    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Container Architecture
```dockerfile
# Multi-stage build for production optimization
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# Security: Non-root user
RUN useradd -m -u 1000 foodxchange
USER foodxchange

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:9000/health || exit 1

# Start application
CMD ["uvicorn", "foodxchange.main:app", "--host", "0.0.0.0", "--port", "9000"]
```

## Performance Architecture

### Caching Strategy
```python
# Multi-level caching approach:

1. Redis Distributed Cache
   - User sessions and authentication tokens
   - API response caching
   - Rate limiting counters
   - Temporary data storage

2. Application-level Caching
   - Template compilation results
   - Database query results
   - Static configuration data
   - AI analysis results

3. Database Optimization
   - Connection pooling
   - Query optimization with indexes
   - Read replicas for analytics
   - Automatic vacuum and maintenance
```

### Scalability Patterns
```python
# Horizontal Scaling
- Stateless application design
- Load balancer distribution
- Database connection pooling
- Shared Redis cache

# Performance Monitoring
- Response time tracking
- Database query performance
- Memory and CPU utilization
- AI service latency monitoring
```

## Monitoring & Observability

### Logging Architecture
```python
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

# Structured logging with correlation IDs
logger = logging.getLogger("foodxchange")

# Azure Application Insights integration
configure_azure_monitor(
    connection_string="InstrumentationKey=your-key"
)

# Log levels and categorization:
- ERROR: System errors and exceptions
- WARNING: Business logic warnings
- INFO: Request/response and business events
- DEBUG: Detailed debugging information
```

### Health Check System
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "database": await check_database_health(),
            "redis": await check_redis_health(),
            "azure_ai": await check_ai_services_health()
        }
    }
```

### Metrics and Alerting
```python
# Key Performance Indicators (KPIs):
- Response time percentiles (P50, P95, P99)
- Error rate by endpoint
- Authentication success/failure rates
- AI service response times
- Database query performance
- Active user sessions
- File upload success rates
```

## Future Architecture Considerations

### Microservices Migration Path
```
Current Monolith → Gradual Decomposition:

1. Authentication Service
2. AI Analysis Service  
3. Project Management Service
4. User Management Service
5. File Processing Service
```

### Event-Driven Architecture
```python
# Future event system for better decoupling:
- User events (registration, login, profile updates)
- Project events (creation, status changes, completion)
- AI events (analysis completed, errors)
- System events (health checks, performance alerts)
```

### API Evolution
```python
# API versioning strategy:
- URL-based versioning (/api/v1/, /api/v2/)
- Header-based versioning
- Backward compatibility maintenance
- Deprecation timeline management
```

---

*This architecture documentation provides a comprehensive overview of the FoodXchange platform's technical foundation and design principles.*