"""
Base repository pattern implementation
"""

from typing import Generic, TypeVar, Optional, List, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DeclarativeMeta)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseRepository(Generic[T, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Get single record by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            return None
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """Get single record by field value"""
        try:
            field = getattr(self.model, field_name)
            return self.db.query(self.model).filter(field == value).first()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by {field_name}: {e}")
            return None
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[T]:
        """Get multiple records with pagination and filtering"""
        try:
            query = self.db.query(self.model)
            
            # Apply filters
            if filters:
                for field_name, value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        if isinstance(value, list):
                            query = query.filter(field.in_(value))
                        elif isinstance(value, dict) and 'like' in value:
                            query = query.filter(field.ilike(f"%{value['like']}%"))
                        else:
                            query = query.filter(field == value)
            
            # Apply ordering
            if order_by:
                if order_by.startswith('-'):
                    field_name = order_by[1:]
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        query = query.order_by(field.desc())
                else:
                    if hasattr(self.model, order_by):
                        field = getattr(self.model, order_by)
                        query = query.order_by(field)
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            return []
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get count of records with optional filtering"""
        try:
            query = self.db.query(func.count(self.model.id))
            
            if filters:
                for field_name, value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        if isinstance(value, list):
                            query = query.filter(field.in_(value))
                        elif isinstance(value, dict) and 'like' in value:
                            query = query.filter(field.ilike(f"%{value['like']}%"))
                        else:
                            query = query.filter(field == value)
            
            return query.scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            return 0
    
    async def create(self, obj_in: CreateSchemaType) -> Optional[T]:
        """Create new record"""
        try:
            obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            self.db.rollback()
            return None
    
    async def update(self, db_obj: T, obj_in: UpdateSchemaType) -> Optional[T]:
        """Update existing record"""
        try:
            obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
            
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            self.db.rollback()
            return None
    
    async def delete(self, id: int) -> bool:
        """Delete record by ID"""
        try:
            db_obj = await self.get_by_id(id)
            if db_obj:
                self.db.delete(db_obj)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {e}")
            self.db.rollback()
            return False
    
    async def bulk_create(self, objects: List[CreateSchemaType]) -> List[T]:
        """Create multiple records in a single transaction"""
        try:
            db_objects = []
            for obj_in in objects:
                obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
                db_obj = self.model(**obj_data)
                db_objects.append(db_obj)
            
            self.db.add_all(db_objects)
            self.db.commit()
            
            for db_obj in db_objects:
                self.db.refresh(db_obj)
            
            return db_objects
        except Exception as e:
            logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            self.db.rollback()
            return []
    
    async def search(self, search_term: str, search_fields: List[str]) -> List[T]:
        """Search records across multiple fields"""
        try:
            query = self.db.query(self.model)
            
            # Build OR conditions for each search field
            conditions = []
            for field_name in search_fields:
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    conditions.append(field.ilike(f"%{search_term}%"))
            
            if conditions:
                query = query.filter(or_(*conditions))
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error searching {self.model.__name__}: {e}")
            return []
    
    async def exists(self, **kwargs) -> bool:
        """Check if record exists with given criteria"""
        try:
            query = self.db.query(self.model)
            
            for field_name, value in kwargs.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    query = query.filter(field == value)
            
            return query.first() is not None
            
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__}: {e}")
            return False


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = 1
    per_page: int = 20
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page


class PaginationResult(BaseModel, Generic[T]):
    """Standard pagination result"""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(cls, items: List[T], total: int, pagination: PaginationParams) -> 'PaginationResult[T]':
        total_pages = (total + pagination.per_page - 1) // pagination.per_page
        
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )