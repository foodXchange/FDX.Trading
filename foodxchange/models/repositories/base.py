from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc
from pydantic import BaseModel
from foodxchange.models.base import Base
from foodxchange.schemas.base import PaginationParams, SearchParams
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository with common CRUD operations
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with id {id}: {e}")
            return None
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filters"""
        try:
            query = db.query(self.model)
            
            if filters:
                query = self._apply_filters(query, filters)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            return []
    
    def get_paginated(
        self,
        db: Session,
        pagination: PaginationParams,
        search: Optional[SearchParams] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get paginated results with search and filters"""
        try:
            query = db.query(self.model)
            
            # Apply search
            if search and search.query:
                query = self._apply_search(query, search.query)
            
            # Apply filters
            if filters:
                query = self._apply_filters(query, filters)
            
            # Apply search filters
            if search and search.filters:
                query = self._apply_filters(query, search.filters)
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            if pagination.sort_by:
                sort_column = getattr(self.model, pagination.sort_by, None)
                if sort_column:
                    if pagination.sort_order == "desc":
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            
            # Apply pagination
            skip = (pagination.page - 1) * pagination.size
            items = query.offset(skip).limit(pagination.size).all()
            
            return {
                "items": items,
                "total": total,
                "page": pagination.page,
                "size": pagination.size,
                "pages": (total + pagination.size - 1) // pagination.size
            }
        except Exception as e:
            logger.error(f"Error getting paginated {self.model.__name__}: {e}")
            return {
                "items": [],
                "total": 0,
                "page": pagination.page,
                "size": pagination.size,
                "pages": 0
            }
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        try:
            obj_data = obj_in.dict()
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete a record by ID"""
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            return False
    
    def exists(self, db: Session, id: int) -> bool:
        """Check if a record exists by ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first() is not None
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {e}")
            return False
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters"""
        try:
            query = db.query(self.model)
            if filters:
                query = self._apply_filters(query, filters)
            return query.count()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            return 0
    
    def _apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """Apply filters to query"""
        for field, value in filters.items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                if isinstance(value, (list, tuple)):
                    query = query.filter(column.in_(value))
                elif isinstance(value, dict):
                    # Handle range filters like {"min": 10, "max": 100}
                    if "min" in value:
                        query = query.filter(column >= value["min"])
                    if "max" in value:
                        query = query.filter(column <= value["max"])
                else:
                    query = query.filter(column == value)
        return query
    
    def _apply_search(self, query: Query, search_term: str) -> Query:
        """Apply search to query - override in subclasses for specific search logic"""
        # Default implementation - search in string columns
        search_conditions = []
        for column in self.model.__table__.columns:
            if column.type.python_type == str:
                search_conditions.append(column.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        return query
    
    def bulk_create(self, db: Session, objects: List[CreateSchemaType]) -> List[ModelType]:
        """Create multiple records in bulk"""
        try:
            db_objects = []
            for obj_in in objects:
                obj_data = obj_in.dict()
                db_obj = self.model(**obj_data)
                db_objects.append(db_obj)
            
            db.add_all(db_objects)
            db.commit()
            
            # Refresh all objects to get their IDs
            for obj in db_objects:
                db.refresh(obj)
            
            return db_objects
        except Exception as e:
            db.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise
    
    def bulk_update(
        self, 
        db: Session, 
        objects: List[ModelType], 
        update_data: Dict[str, Any]
    ) -> List[ModelType]:
        """Update multiple records in bulk"""
        try:
            for obj in objects:
                for field, value in update_data.items():
                    if hasattr(obj, field):
                        setattr(obj, field, value)
            
            db.add_all(objects)
            db.commit()
            
            for obj in objects:
                db.refresh(obj)
            
            return objects
        except Exception as e:
            db.rollback()
            logger.error(f"Error bulk updating {self.model.__name__}: {e}")
            raise 