from sqlalchemy import Column, Boolean, DateTime, String, event, Index, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query
from sqlalchemy.sql import func
from datetime import datetime
import json
from foodxchange.database import Base

class TimestampMixin:
    """Add created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SoftDeleteMixin:
    """Add soft delete functionality"""
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by_id = Column(String(50), nullable=True)
    
    @classmethod
    def filter_active(cls, query: Query) -> Query:
        """Filter out soft-deleted records"""
        return query.filter(cls.is_deleted == False)
    
    def soft_delete(self, user_id: str = None):
        """Mark record as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by_id = user_id

class SearchableMixin:
    """Add full-text search capability"""
    search_vector = Column(String, nullable=True)
    
    @declared_attr
    def __table_args__(cls):
        return (
            Index(f'idx_{cls.__tablename__}_search', 'search_vector'),
        )
    
    @classmethod
    def search(cls, query: Query, search_term: str) -> Query:
        """Perform full-text search"""
        return query.filter(
            func.to_tsvector('english', cls.search_vector).op('@@')(
                func.plainto_tsquery('english', search_term)
            )
        )

class VersionMixin:
    """Add versioning capability"""
    version = Column(Integer, default=1, nullable=False)
    
    def increment_version(self):
        """Increment version number"""
        self.version += 1

class AuditMixin:
    """Add audit trail capability"""
    created_by_id = Column(String(50), nullable=True)
    updated_by_id = Column(String(50), nullable=True)
    
    @event.listens_for(Base, 'before_insert')
    def set_created_by(mapper, connection, target):
        """Set created_by on insert"""
        if hasattr(target, 'created_by_id') and not target.created_by_id:
            # Get current user from context (implement based on your auth system)
            target.created_by_id = get_current_user_id()
    
    @event.listens_for(Base, 'before_update')
    def set_updated_by(mapper, connection, target):
        """Set updated_by on update"""
        if hasattr(target, 'updated_by_id'):
            target.updated_by_id = get_current_user_id()

def get_current_user_id():
    """Get current user ID from context - implement based on your auth system"""
    # This should be implemented based on your authentication system
    # For now, return None
    return None 