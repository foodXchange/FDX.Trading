from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base
from passlib.hash import bcrypt
import datetime

Base = declarative_base()

class User(Base):
    """User model for FoodXchange platform."""
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password: str = Column(String(255), nullable=False)
    full_name: str = Column(String(255))
    role: str = Column(String(50), default="buyer")
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime.datetime = Column(DateTime, default=func.now())
    updated_at: datetime.datetime = Column(DateTime, default=func.now(), onupdate=func.now())

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return bcrypt.verify(password, self.hashed_password)

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.hashed_password = bcrypt.hash(password) 