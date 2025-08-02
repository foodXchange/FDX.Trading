# FoodXchange Developer Guide

## Getting Started

This guide provides comprehensive information for developers working on the FoodXchange platform.

## Development Environment Setup

### Prerequisites
- Python 3.11+
- Docker Desktop
- Git
- VS Code or PyCharm (recommended)
- Azure CLI (optional, for cloud features)

### Step 1: Clone and Setup
```bash
# Clone repository
git clone <repository-url>
cd FoodXchange

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Step 2: Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with development settings
# Minimal required configuration:
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/foodxchange
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-development-secret-key-min-32-chars
```

### Step 3: Start Development Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps

# Initialize database (if needed)
python -c "from foodxchange.database import create_tables; create_tables()"
```

### Step 4: Start Development Server
```bash
# Using the clean start script
python start_clean.bat

# Or manually
python -m uvicorn foodxchange.main:app --reload --port 9000 --log-level debug
```

### Step 5: Verify Setup
```bash
# Test health endpoint
curl http://localhost:9000/health

# Test authentication
curl -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=admin@fdx.trading&password=FDX2030!"
```

## Code Organization

### Project Structure
```
foodxchange/
├── main.py                 # FastAPI application entry point
├── config/                 # Configuration management
│   ├── settings.py         # Pydantic settings
│   └── dev_auth.py         # Development authentication
├── core/                   # Core business logic
│   ├── auth.py             # Authentication middleware
│   ├── security.py         # Security utilities
│   ├── exceptions.py       # Custom exceptions
│   └── dependencies.py     # FastAPI dependencies
├── models/                 # Database models
│   ├── base.py             # Base model classes
│   ├── user.py             # User model
│   ├── project_enhanced.py # Project management
│   ├── buyer.py            # Buyer model
│   └── supplier.py         # Supplier model
├── routes/                 # API route handlers
│   ├── auth_routes.py      # Authentication endpoints
│   ├── ai_import_routes.py # AI data import
│   ├── demo_routes.py      # Demo functionality
│   └── footer_routes.py    # Static pages
├── services/               # Business services
│   ├── ai_service.py       # AI integration
│   ├── email_service.py    # Email notifications
│   └── error_handling/     # Error management
├── middleware/             # Request middleware
│   └── rate_limiting.py    # Rate limiting
├── templates/              # Jinja2 templates
│   ├── base.html           # Base template
│   ├── components/         # UI components
│   └── pages/              # Page templates
└── static/                 # Static assets
    ├── css/                # Stylesheets
    ├── js/                 # JavaScript
    └── brand/              # Fonts and logos
```

### Coding Standards

#### Python Style Guide
```python
# Follow PEP 8 with these specific guidelines:

# 1. Imports
from typing import Dict, List, Optional
import logging
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

# 2. Function definitions with type hints
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_database)
) -> User:
    """Create a new user with validation."""
    pass

# 3. Class definitions
class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email address."""
        pass

# 4. Error handling
try:
    result = await some_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise HTTPException(status_code=400, detail="Operation failed")
```

#### Database Models
```python
# models/base.py
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

# models/user.py
class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    # ... other fields
```

#### API Route Patterns
```python
# routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.auth import get_current_user
from ..services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get current user profile."""
    user_service = UserService(db)
    return await user_service.get_profile(current_user.id)

@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update user profile."""
    user_service = UserService(db)
    return await user_service.update_profile(current_user.id, profile_data)
```

## Development Workflow

### Git Workflow
```bash
# 1. Create feature branch
git checkout -b feature/user-profile-enhancement

# 2. Make changes with descriptive commits
git add .
git commit -m "feat: Add user profile image upload functionality"

# 3. Push and create pull request
git push origin feature/user-profile-enhancement

# 4. Code review and merge
```

### Testing Strategy
```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from foodxchange.main import app
from foodxchange.database import get_database, Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost:5433/test_foodxchange"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_database] = override_get_db
client = TestClient(app)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }

def test_user_registration(test_user):
    response = client.post("/auth/signup", data=test_user)
    assert response.status_code == 303
    assert "access_token" in response.cookies

def test_user_login(test_user):
    # First register user
    client.post("/auth/signup", data=test_user)
    
    # Then test login
    response = client.post("/auth/login", data={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 303
    assert "access_token" in response.cookies
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=foodxchange --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_auth"
```

## AI Service Development

### Adding New AI Features
```python
# services/ai_service.py
class AIService:
    def __init__(self):
        self.openai_client = openai.AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version="2024-02-01",
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
    
    async def analyze_product_nutrition(self, product_data: Dict) -> NutritionAnalysis:
        """Analyze product nutrition information using AI."""
        try:
            prompt = self._build_nutrition_prompt(product_data)
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": "You are a nutrition expert..."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            return self._parse_nutrition_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI nutrition analysis failed: {e}")
            raise AIServiceException("Nutrition analysis failed")
    
    def _build_nutrition_prompt(self, product_data: Dict) -> str:
        """Build prompt for nutrition analysis."""
        return f"""
        Analyze the nutrition information for this product:
        Name: {product_data.get('name')}
        Ingredients: {product_data.get('ingredients')}
        
        Please provide:
        1. Nutritional assessment
        2. Health benefits
        3. Dietary restrictions
        4. Allergen information
        """
```

### AI Error Handling
```python
# services/error_handling/ai_error_handler.py
class AIServiceException(Exception):
    """Custom exception for AI service errors."""
    pass

async def handle_ai_service_error(error: Exception) -> Dict:
    """Standardized AI error handling."""
    if isinstance(error, openai.RateLimitError):
        return {
            "error": "rate_limit_exceeded",
            "message": "AI service rate limit exceeded. Please try again later.",
            "retry_after": 60
        }
    elif isinstance(error, openai.AuthenticationError):
        return {
            "error": "authentication_failed",
            "message": "AI service authentication failed."
        }
    else:
        return {
            "error": "ai_service_error",
            "message": "AI service temporarily unavailable."
        }
```

## Database Development

### Creating Migrations
```bash
# Install Alembic
pip install alembic

# Initialize Alembic (if not done)
alembic init alembic

# Create new migration
alembic revision --autogenerate -m "Add user profile fields"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Database Best Practices
```python
# models/mixins.py
class BaseModel:
    """Base model with common functionality."""
    
    @classmethod
    def create(cls, db: Session, **kwargs):
        """Create new instance."""
        instance = cls(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    
    def update(self, db: Session, **kwargs):
        """Update instance."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.commit()
        db.refresh(self)
        return self
    
    def delete(self, db: Session):
        """Soft delete instance."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.commit()

# Repository pattern
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        return User.create(self.db, **user_data.dict())
```

## Frontend Development

### Template Development
```html
<!-- templates/components/user_card.html -->
<div class="user-card" data-user-id="{{ user.id }}">
    <div class="user-avatar">
        {% if user.avatar_url %}
            <img src="{{ user.avatar_url }}" alt="{{ user.name }}" class="avatar-img">
        {% else %}
            <div class="avatar-placeholder">{{ user.name[0] }}</div>
        {% endif %}
    </div>
    
    <div class="user-info">
        <h3 class="user-name">{{ user.first_name }} {{ user.last_name }}</h3>
        <p class="user-company">{{ user.company }}</p>
        <span class="user-role badge badge-{{ user.role }}">{{ user.role.title() }}</span>
    </div>
    
    <div class="user-actions">
        {% if current_user.is_admin %}
            <button class="btn btn-sm btn-outline-primary" onclick="editUser({{ user.id }})">
                Edit
            </button>
        {% endif %}
    </div>
</div>
```

### JavaScript Development
```javascript
// static/js/modules/user-management.js
class UserManagement {
    constructor() {
        this.apiBase = '/api/users';
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadUsers();
    }
    
    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="edit-user"]')) {
                this.editUser(e.target.dataset.userId);
            }
        });
    }
    
    async loadUsers() {
        try {
            const response = await fetch(`${this.apiBase}/`);
            const users = await response.json();
            this.renderUsers(users);
        } catch (error) {
            console.error('Failed to load users:', error);
            this.showError('Failed to load users');
        }
    }
    
    async editUser(userId) {
        try {
            const modal = new UserEditModal(userId);
            await modal.show();
        } catch (error) {
            console.error('Failed to edit user:', error);
        }
    }
    
    renderUsers(users) {
        const container = document.getElementById('users-container');
        container.innerHTML = users.map(user => `
            <div class="user-card" data-user-id="${user.id}">
                <!-- User card content -->
            </div>
        `).join('');
    }
    
    showError(message) {
        // Show error notification
        const notification = new Notification('error', message);
        notification.show();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new UserManagement();
});
```

## Security Development

### Authentication Middleware
```python
# core/auth.py
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> User:
    """Get current authenticated user."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### Input Validation
```python
# schemas/user_schemas.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v) > 50:
            raise ValueError('Name cannot exceed 50 characters')
        return v.strip()

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    
    @validator('*', pre=True)
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip() if v else None
        return v
```

## Performance Optimization

### Caching Implementation
```python
# core/cache.py
import redis
from typing import Optional, Any
import json
import pickle

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            serialized = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False

# Usage in services
class UserService:
    def __init__(self, db: Session, cache: CacheService):
        self.db = db
        self.cache = cache
    
    async def get_user_profile(self, user_id: int) -> UserProfile:
        """Get user profile with caching."""
        cache_key = f"user_profile:{user_id}"
        
        # Try cache first
        cached_profile = await self.cache.get(cache_key)
        if cached_profile:
            return cached_profile
        
        # Fallback to database
        profile = self.db.query(User).filter(User.id == user_id).first()
        if profile:
            await self.cache.set(cache_key, profile, ttl=1800)  # 30 minutes
        
        return profile
```

### Database Optimization
```python
# models/optimized_queries.py
from sqlalchemy.orm import joinedload, selectinload

class OptimizedUserService:
    @staticmethod
    def get_users_with_projects(db: Session) -> List[User]:
        """Get users with their projects in a single query."""
        return db.query(User).options(
            selectinload(User.projects)
        ).filter(User.is_active == True).all()
    
    @staticmethod
    def get_user_dashboard_data(db: Session, user_id: int) -> User:
        """Get user with all dashboard-related data."""
        return db.query(User).options(
            joinedload(User.projects).joinedload(Project.buyers),
            selectinload(User.notifications)
        ).filter(User.id == user_id).first()
```

## Debugging and Logging

### Development Logging
```python
# core/logging.py
import logging
import sys
from pathlib import Path

def setup_logging():
    """Configure logging for development."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    log_file = Path("logs/foodxchange.log")
    log_file.parent.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Usage in modules
logger = logging.getLogger(__name__)

async def some_function():
    logger.info("Function started")
    try:
        result = await some_operation()
        logger.debug(f"Operation result: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

### Debug Tools
```python
# utils/debug.py
import time
import functools
from typing import Callable

def debug_timer(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper

def debug_sql_queries(db: Session):
    """Enable SQL query logging for debugging."""
    import logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## Contributing Guidelines

### Code Review Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints and docstrings
- [ ] Tests are written for new functionality
- [ ] Security considerations are addressed
- [ ] Performance impact is considered
- [ ] Documentation is updated
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate and informative

### Pull Request Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Security
- [ ] Security impact assessed
- [ ] Input validation added
- [ ] Authentication/authorization considered

## Performance
- [ ] Performance impact evaluated
- [ ] Database queries optimized
- [ ] Caching implemented where appropriate
```

---

*This developer guide provides the foundation for contributing to the FoodXchange platform. For questions or clarifications, please refer to the architecture documentation or contact the development team.*