from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc
from foodxchange.models.user import User
from foodxchange.schemas.user import UserCreate, UserUpdate, UserRole
from foodxchange.repositories.base import BaseRepository
import bcrypt
import logging

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for User model with authentication and role-based operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_by_role(self, db: Session, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        try:
            return db.query(User).filter(
                User.role == role,
                User.is_active == True
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            return []
    
    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        try:
            return db.query(User).filter(
                User.is_active == True
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = self.get_by_email(db, email)
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            return user
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """Create a new user with hashed password"""
        try:
            # Hash the password
            hashed_password = self.hash_password(user_in.password)
            
            # Create user data without password
            user_data = user_in.dict(exclude={'password'})
            user_data['hashed_password'] = hashed_password
            
            # Create user object
            db_user = User(**user_data)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return db_user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    def update_user(self, db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """Update user with optional password hashing"""
        try:
            user = self.get(db, user_id)
            if not user:
                return None
            
            # Handle password update if provided
            update_data = user_in.dict(exclude_unset=True)
            if 'password' in update_data:
                update_data['hashed_password'] = self.hash_password(update_data.pop('password'))
            
            # Update user
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    def change_password(self, db: Session, user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.get(db, user_id)
            if not user:
                return False
            
            user.hashed_password = self.hash_password(new_password)
            db.add(user)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error changing password for user {user_id}: {e}")
            return False
    
    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Deactivate a user"""
        try:
            user = self.get(db, user_id)
            if not user:
                return False
            
            user.is_active = False
            db.add(user)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False
    
    def activate_user(self, db: Session, user_id: int) -> bool:
        """Activate a user"""
        try:
            user = self.get(db, user_id)
            if not user:
                return False
            
            user.is_active = True
            db.add(user)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error activating user {user_id}: {e}")
            return False
    
    def update_last_login(self, db: Session, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            from datetime import datetime
            user = self.get(db, user_id)
            if not user:
                return False
            
            user.last_login = datetime.utcnow()
            db.add(user)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False
    
    def get_users_by_department(self, db: Session, department: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by department"""
        try:
            return db.query(User).filter(
                User.department == department,
                User.is_active == True
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting users by department {department}: {e}")
            return []
    
    def search_users(self, db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by name, email, or department"""
        try:
            return db.query(User).filter(
                or_(
                    User.full_name.ilike(f"%{search_term}%"),
                    User.email.ilike(f"%{search_term}%"),
                    User.department.ilike(f"%{search_term}%")
                ),
                User.is_active == True
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching users with term {search_term}: {e}")
            return []
    
    def get_user_stats(self, db: Session) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            inactive_users = total_users - active_users
            
            # Count by role
            role_counts = {}
            for role in UserRole:
                count = db.query(User).filter(User.role == role).count()
                role_counts[role.value] = count
            
            # Count by department
            department_counts = db.query(
                User.department,
                db.func.count(User.id)
            ).filter(
                User.department.isnot(None)
            ).group_by(User.department).all()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "role_counts": role_counts,
                "department_counts": dict(department_counts)
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "role_counts": {},
                "department_counts": {}
            }
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _apply_search(self, query: Query, search_term: str) -> Query:
        """Apply search to user query"""
        return query.filter(
            or_(
                User.full_name.ilike(f"%{search_term}%"),
                User.email.ilike(f"%{search_term}%"),
                User.department.ilike(f"%{search_term}%")
            )
        ) 