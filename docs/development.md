# FoodXchange Development Guide

## Overview

This guide covers the development workflow, coding standards, and best practices for contributing to the FoodXchange platform.

## Development Environment Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Node.js 16+ (for frontend assets)
- Git
- VS Code (recommended)

### Initial Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/foodxchange.git
cd foodxchange
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up development environment**
```bash
cp .env.example .env
# Edit .env with your development configuration
```

4. **Initialize database**
```bash
python setup_database.py
```

5. **Start development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
foodxchange/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── supplier.py
│   │   ├── rfq.py
│   │   ├── quote.py
│   │   └── email.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── supplier.py
│   │   ├── rfq.py
│   │   ├── quote.py
│   │   └── email.py
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── email_service.py
│   │   ├── rfq_service.py
│   │   ├── quote_service.py
│   │   ├── supplier_service.py
│   │   └── notification_service.py
│   ├── routes/              # Route handlers
│   │   ├── __init__.py
│   │   └── agent_routes.py
│   ├── agents/              # Agent management
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── supplier.py
│   │   ├── rfq.py
│   │   ├── quote.py
│   │   └── email.py
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── landing.html
│   │   ├── dashboard.html
│   │   ├── suppliers.html
│   │   ├── rfq_new.html
│   │   ├── analytics.html
│   │   ├── email_intelligence.html
│   │   ├── quote_comparison.html
│   │   ├── projects.html
│   │   ├── agent_dashboard.html
│   │   └── operator_dashboard.html
│   └── static/              # Static assets
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/              # Database migrations
├── docs/                    # Documentation
├── data/                    # Data files and exports
├── uploads/                 # File uploads
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies
├── alembic.ini             # Alembic configuration
├── setup_database.py       # Database setup script
└── README.md               # Project documentation
```

## Coding Standards

### Python Code Style

Follow PEP 8 guidelines with these specific rules:

1. **Import Organization**
```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

# Local imports
from app.models.user import User
from app.schemas.user import UserCreate
```

2. **Function and Class Naming**
```python
# Use snake_case for functions and variables
def get_user_by_email(email: str) -> Optional[User]:
    pass

# Use PascalCase for classes
class UserService:
    pass

# Use UPPER_CASE for constants
MAX_RETRY_ATTEMPTS = 3
```

3. **Type Hints**
```python
from typing import List, Dict, Optional, Union

def create_user(user_data: UserCreate, db: Session) -> User:
    pass

def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    pass
```

### Database Models

1. **Model Structure**
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

2. **Relationships**
```python
from sqlalchemy.orm import relationship

class RFQ(Base):
    __tablename__ = "rfqs"
    
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    buyer = relationship("User", back_populates="rfqs")
    quotes = relationship("Quote", back_populates="rfq")
```

### API Endpoints

1. **Route Structure**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/users/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """Get list of users with pagination."""
    users = user_repository.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/users/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """Create a new user."""
    user = user_repository.create(db, obj_in=user_data)
    return user
```

2. **Error Handling**
```python
from fastapi import HTTPException

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_repository.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Service Layer

1. **Service Structure**
```python
from typing import Optional, List
from sqlalchemy.orm import Session

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user with validation."""
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(db, email=user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = self.user_repository.create(db, obj_in=user_data)
        return user
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repository.get(db, id=user_id)
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Test configuration and fixtures
├── test_api/                # API endpoint tests
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_suppliers.py
│   ├── test_rfqs.py
│   └── test_quotes.py
├── test_services/           # Service layer tests
│   ├── test_auth_service.py
│   ├── test_email_service.py
│   └── test_rfq_service.py
├── test_models/             # Model tests
│   ├── test_user.py
│   └── test_supplier.py
└── test_utils/              # Utility function tests
```

### Writing Tests

1. **Test Configuration**
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

2. **API Tests**
```python
# tests/test_api/test_users.py
import pytest
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data

def test_get_user_not_found(client: TestClient):
    response = client.get("/users/999")
    assert response.status_code == 404
```

3. **Service Tests**
```python
# tests/test_services/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate

def test_create_user_success(db):
    auth_service = AuthService()
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword",
        full_name="Test User"
    )
    
    user = auth_service.register_user(db, user_data)
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name

def test_create_user_duplicate_email(db):
    auth_service = AuthService()
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword",
        full_name="Test User"
    )
    
    # Create first user
    auth_service.register_user(db, user_data)
    
    # Try to create duplicate
    with pytest.raises(ValueError, match="User with this email already exists"):
        auth_service.register_user(db, user_data)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api/test_users.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

## Database Migrations

### Creating Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current
```

### Migration Best Practices

1. **Always test migrations**
```bash
# Test migration on development database
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

2. **Use descriptive migration names**
```bash
alembic revision --autogenerate -m "Add supplier verification fields"
```

3. **Review auto-generated migrations**
```python
# Always review the generated migration file
# Make sure it captures all intended changes
```

## Frontend Development

### Template Structure

1. **Base Template**
```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}FoodXchange{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', path='css/main.css') }}">
</head>
<body>
    <nav>
        <!-- Navigation -->
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <script src="{{ url_for('static', path='js/main.js') }}"></script>
</body>
</html>
```

2. **Page Templates**
```html
<!-- app/templates/dashboard.html -->
{% extends "base.html" %}

{% block title %}Dashboard - FoodXchange{% endblock %}

{% block content %}
<div class="dashboard">
    <h1>Dashboard</h1>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Suppliers</h3>
            <p class="stat-number">{{ stats.suppliers }}</p>
        </div>
        <!-- More stat cards -->
    </div>
</div>
{% endblock %}
```

### Static Assets

1. **CSS Organization**
```css
/* app/static/css/main.css */
/* Base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Component styles */
.dashboard {
    padding: 2rem;
}

.stat-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

2. **JavaScript Organization**
```javascript
// app/static/js/main.js
// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Event handlers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize application
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    // Load initial data
    loadDashboardData();
}
```

## Git Workflow

### Branch Naming

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(auth): add JWT authentication
fix(api): resolve supplier listing pagination issue
docs(readme): update installation instructions
refactor(services): improve error handling in email service
```

### Pull Request Process

1. **Create feature branch**
```bash
git checkout -b feature/user-authentication
```

2. **Make changes and commit**
```bash
git add .
git commit -m "feat(auth): implement user authentication"
```

3. **Push and create PR**
```bash
git push origin feature/user-authentication
```

4. **Code review checklist**
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed

## Debugging

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug information")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error message")
```

### Debug Mode

```bash
# Enable debug mode
export DEBUG=True
uvicorn app.main:app --reload --log-level debug
```

### Database Debugging

```python
# Enable SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## Performance Optimization

### Database Optimization

1. **Use indexes**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Index for fast lookups
```

2. **Optimize queries**
```python
# Use select_from for complex joins
from sqlalchemy.orm import selectinload

users = db.query(User).options(selectinload(User.rfqs)).all()
```

### Caching

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiry=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            result = redis_client.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                redis_client.setex(cache_key, expiry, str(result))
            
            return result
        return wrapper
    return decorator
```

## Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```

### SQL Injection Prevention

```python
# Use parameterized queries (SQLAlchemy handles this automatically)
user = db.query(User).filter(User.email == email).first()

# Don't do this:
# user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(user_id)
    if user is None:
        raise credentials_exception
    return user
```

## Support and Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

### Community
- FastAPI Discord: https://discord.gg/VQjSZaeJmf
- SQLAlchemy Mailing List: https://groups.google.com/forum/#!forum/sqlalchemy

### Internal Resources
- API Documentation: http://localhost:8000/docs
- Development Wiki: [Internal Wiki Link]
- Issue Tracker: [GitHub Issues]

For development questions:
- Email: dev@foodxchange.com
- Slack: #foodxchange-dev 