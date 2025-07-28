"""
Simple Authentication System for FoodXchange
Using JWT tokens with secure password hashing
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT settings
SECRET_KEY = settings.secret_key or "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Dependency for routes that require admin access
async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Ensure the current user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Simple session-based auth for templates (non-API routes)
class SessionAuth:
    """Simple session authentication for template rendering"""
    
    @staticmethod
    def create_session(response, user: User):
        """Create a session cookie"""
        token = create_access_token(data={"sub": user.email})
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            secure=settings.use_https,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    def get_current_user_from_cookie(request, db: Session) -> Optional[User]:
        """Get user from session cookie"""
        token = request.cookies.get("session_token")
        if not token:
            return None
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            
            user = db.query(User).filter(User.email == email).first()
            return user
        except JWTError:
            return None
    
    @staticmethod
    def clear_session(response):
        """Clear the session cookie"""
        response.delete_cookie("session_token")


# Helper function for templates
def get_current_user_context(request, db: Session) -> dict:
    """Get user context for template rendering"""
    user = SessionAuth.get_current_user_from_cookie(request, db)
    if user:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin,
            "initials": "".join([n[0].upper() for n in user.name.split()[:2]])
        }
    return None