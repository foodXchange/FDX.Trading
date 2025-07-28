from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc, func
from app.models.supplier import Supplier, SupplierProduct, SupplierCertification
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierStatus
from app.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class SupplierRepository(BaseRepository[Supplier, SupplierCreate, SupplierUpdate]):
    """Repository for Supplier model with search, filtering, and enrichment operations"""
    
    def __init__(self):
        super().__init__(Supplier)
    
    def get_by_email(self, db: Session, email: str) -> Optional[Supplier]:
        """Get supplier by email address"""
        try:
            return db.query(Supplier).filter(Supplier.email == email).first()
        except Exception as e:
            logger.error(f"Error getting supplier by email {email}: {e}")
            return None
    
    def get_by_company_name(self, db: Session, company_name: str) -> Optional[Supplier]:
        """Get supplier by company name"""
        try:
            return db.query(Supplier).filter(Supplier.company_name == company_name).first()
        except Exception as e:
            logger.error(f"Error getting supplier by company name {company_name}: {e}")
            return None
    
    def get_by_status(self, db: Session, status: SupplierStatus, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get suppliers by status"""
        try:
            return db.query(Supplier).filter(
                Supplier.status == status
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting suppliers by status {status}: {e}")
            return []
    
    def get_by_country(self, db: Session, country: str, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get suppliers by country"""
        try:
            return db.query(Supplier).filter(
                Supplier.country == country,
                Supplier.status == SupplierStatus.ACTIVE
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting suppliers by country {country}: {e}")
            return []
    
    def get_by_category(self, db: Session, category: str, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get suppliers by product category"""
        try:
            return db.query(Supplier).filter(
                Supplier.categories.contains([category]),
                Supplier.status == SupplierStatus.ACTIVE
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting suppliers by category {category}: {e}")
            return []
    
    def get_verified_suppliers(self, db: Session, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get verified suppliers"""
        try:
            return db.query(Supplier).filter(
                Supplier.is_verified == True,
                Supplier.status == SupplierStatus.ACTIVE
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting verified suppliers: {e}")
            return []
    
    def search_suppliers(self, db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Search suppliers by company name, email, or categories"""
        try:
            return db.query(Supplier).filter(
                or_(
                    Supplier.company_name.ilike(f"%{search_term}%"),
                    Supplier.email.ilike(f"%{search_term}%"),
                    Supplier.categories.overlap([search_term])
                ),
                Supplier.status == SupplierStatus.ACTIVE
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching suppliers with term {search_term}: {e}")
            return []
    
    def get_suppliers_with_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get suppliers with their products"""
        try:
            return db.query(Supplier).options(
                db.joinedload(Supplier.products)
            ).filter(
                Supplier.status == SupplierStatus.ACTIVE
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting suppliers with products: {e}")
            return []
    
    def get_supplier_with_details(self, db: Session, supplier_id: int) -> Optional[Supplier]:
        """Get supplier with all related details"""
        try:
            return db.query(Supplier).options(
                db.joinedload(Supplier.products),
                db.joinedload(Supplier.certifications)
            ).filter(Supplier.id == supplier_id).first()
        except Exception as e:
            logger.error(f"Error getting supplier details for {supplier_id}: {e}")
            return None
    
    def update_supplier_rating(self, db: Session, supplier_id: int, new_rating: float) -> bool:
        """Update supplier rating"""
        try:
            supplier = self.get(db, supplier_id)
            if not supplier:
                return False
            
            supplier.rating = new_rating
            db.add(supplier)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating rating for supplier {supplier_id}: {e}")
            return False
    
    def update_response_metrics(self, db: Session, supplier_id: int, response_time: float) -> bool:
        """Update supplier response metrics"""
        try:
            supplier = self.get(db, supplier_id)
            if not supplier:
                return False
            
            # Update response rate and average response time
            if supplier.response_rate is None:
                supplier.response_rate = 100
            else:
                supplier.response_rate = min(100, supplier.response_rate + 1)
            
            if supplier.average_response_time is None:
                supplier.average_response_time = response_time
            else:
                # Simple moving average
                supplier.average_response_time = (supplier.average_response_time + response_time) / 2
            
            db.add(supplier)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating response metrics for supplier {supplier_id}: {e}")
            return False
    
    def mark_as_verified(self, db: Session, supplier_id: int) -> bool:
        """Mark supplier as verified"""
        try:
            from datetime import datetime
            supplier = self.get(db, supplier_id)
            if not supplier:
                return False
            
            supplier.is_verified = True
            supplier.verified_date = datetime.utcnow()
            db.add(supplier)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking supplier {supplier_id} as verified: {e}")
            return False
    
    def get_supplier_products(self, db: Session, supplier_id: int) -> List[SupplierProduct]:
        """Get all products for a supplier"""
        try:
            return db.query(SupplierProduct).filter(
                SupplierProduct.supplier_id == supplier_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting products for supplier {supplier_id}: {e}")
            return []
    
    def get_supplier_certifications(self, db: Session, supplier_id: int) -> List[SupplierCertification]:
        """Get all certifications for a supplier"""
        try:
            return db.query(SupplierCertification).filter(
                SupplierCertification.supplier_id == supplier_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting certifications for supplier {supplier_id}: {e}")
            return []
    
    def get_supplier_stats(self, db: Session) -> Dict[str, Any]:
        """Get supplier statistics"""
        try:
            total_suppliers = db.query(Supplier).count()
            active_suppliers = db.query(Supplier).filter(Supplier.status == SupplierStatus.ACTIVE).count()
            verified_suppliers = db.query(Supplier).filter(Supplier.is_verified == True).count()
            
            # Count by status
            status_counts = db.query(
                Supplier.status,
                func.count(Supplier.id)
            ).group_by(Supplier.status).all()
            
            # Count by country
            country_counts = db.query(
                Supplier.country,
                func.count(Supplier.id)
            ).filter(
                Supplier.country.isnot(None)
            ).group_by(Supplier.country).all()
            
            # Average rating
            avg_rating = db.query(func.avg(Supplier.rating)).scalar()
            
            # Average response rate
            avg_response_rate = db.query(func.avg(Supplier.response_rate)).scalar()
            
            return {
                "total_suppliers": total_suppliers,
                "active_suppliers": active_suppliers,
                "verified_suppliers": verified_suppliers,
                "status_counts": dict(status_counts),
                "country_counts": dict(country_counts),
                "average_rating": float(avg_rating) if avg_rating else 0.0,
                "average_response_rate": float(avg_response_rate) if avg_response_rate else 0.0
            }
        except Exception as e:
            logger.error(f"Error getting supplier stats: {e}")
            return {
                "total_suppliers": 0,
                "active_suppliers": 0,
                "verified_suppliers": 0,
                "status_counts": {},
                "country_counts": {},
                "average_rating": 0.0,
                "average_response_rate": 0.0
            }
    
    def get_top_suppliers(self, db: Session, limit: int = 10) -> List[Supplier]:
        """Get top suppliers by rating"""
        try:
            return db.query(Supplier).filter(
                Supplier.status == SupplierStatus.ACTIVE,
                Supplier.rating.isnot(None)
            ).order_by(desc(Supplier.rating)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting top suppliers: {e}")
            return []
    
    def get_suppliers_by_rating_range(self, db: Session, min_rating: float, max_rating: float) -> List[Supplier]:
        """Get suppliers within a rating range"""
        try:
            return db.query(Supplier).filter(
                Supplier.rating >= min_rating,
                Supplier.rating <= max_rating,
                Supplier.status == SupplierStatus.ACTIVE
            ).all()
        except Exception as e:
            logger.error(f"Error getting suppliers by rating range: {e}")
            return []
    
    def _apply_search(self, query: Query, search_term: str) -> Query:
        """Apply search to supplier query"""
        return query.filter(
            or_(
                Supplier.company_name.ilike(f"%{search_term}%"),
                Supplier.email.ilike(f"%{search_term}%"),
                Supplier.categories.overlap([search_term])
            )
        ) 