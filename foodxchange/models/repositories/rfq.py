from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc, func
from foodxchange.models.rfq import RFQ, RFQSupplier
from foodxchange.schemas.rfq import RFQCreate, RFQUpdate, RFQStatus
from foodxchange.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class RFQRepository(BaseRepository[RFQ, RFQCreate, RFQUpdate]):
    """Repository for RFQ model with status management and supplier operations"""
    
    def __init__(self):
        super().__init__(RFQ)
    
    def get_by_buyer(self, db: Session, buyer_id: int, skip: int = 0, limit: int = 100) -> List[RFQ]:
        """Get RFQs by buyer"""
        try:
            return db.query(RFQ).filter(
                RFQ.buyer_id == buyer_id
            ).order_by(desc(RFQ.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting RFQs by buyer {buyer_id}: {e}")
            return []
    
    def get_by_status(self, db: Session, status: RFQStatus, skip: int = 0, limit: int = 100) -> List[RFQ]:
        """Get RFQs by status"""
        try:
            return db.query(RFQ).filter(
                RFQ.status == status
            ).order_by(desc(RFQ.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting RFQs by status {status}: {e}")
            return []
    
    def get_active_rfqs(self, db: Session, skip: int = 0, limit: int = 100) -> List[RFQ]:
        """Get active RFQs (not completed or cancelled)"""
        try:
            return db.query(RFQ).filter(
                RFQ.status.in_([
                    RFQStatus.DRAFT,
                    RFQStatus.SENT,
                    RFQStatus.RECEIVING_QUOTES,
                    RFQStatus.UNDER_REVIEW
                ])
            ).order_by(desc(RFQ.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting active RFQs: {e}")
            return []
    
    def get_rfq_with_details(self, db: Session, rfq_id: int) -> Optional[RFQ]:
        """Get RFQ with all related details"""
        try:
            return db.query(RFQ).options(
                db.joinedload(RFQ.line_items),
                db.joinedload(RFQ.suppliers)
            ).filter(RFQ.id == rfq_id).first()
        except Exception as e:
            logger.error(f"Error getting RFQ details for {rfq_id}: {e}")
            return None
    
    def update_status(self, db: Session, rfq_id: int, new_status: RFQStatus) -> bool:
        """Update RFQ status"""
        try:
            rfq = self.get(db, rfq_id)
            if not rfq:
                return False
            
            rfq.status = new_status
            db.add(rfq)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating status for RFQ {rfq_id}: {e}")
            return False
    
    def add_supplier(self, db: Session, rfq_id: int, supplier_id: int) -> bool:
        """Add supplier to RFQ"""
        try:
            # Check if supplier is already added
            existing = db.query(RFQSupplier).filter(
                RFQSupplier.rfq_id == rfq_id,
                RFQSupplier.supplier_id == supplier_id
            ).first()
            
            if existing:
                return True  # Already exists
            
            rfq_supplier = RFQSupplier(
                rfq_id=rfq_id,
                supplier_id=supplier_id,
                status="invited"
            )
            db.add(rfq_supplier)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding supplier {supplier_id} to RFQ {rfq_id}: {e}")
            return False
    
    def remove_supplier(self, db: Session, rfq_id: int, supplier_id: int) -> bool:
        """Remove supplier from RFQ"""
        try:
            rfq_supplier = db.query(RFQSupplier).filter(
                RFQSupplier.rfq_id == rfq_id,
                RFQSupplier.supplier_id == supplier_id
            ).first()
            
            if rfq_supplier:
                db.delete(rfq_supplier)
                db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error removing supplier {supplier_id} from RFQ {rfq_id}: {e}")
            return False
    
    def get_rfq_suppliers(self, db: Session, rfq_id: int) -> List[RFQSupplier]:
        """Get all suppliers for an RFQ"""
        try:
            return db.query(RFQSupplier).filter(
                RFQSupplier.rfq_id == rfq_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting suppliers for RFQ {rfq_id}: {e}")
            return []
    
    def get_rfq_stats(self, db: Session) -> Dict[str, Any]:
        """Get RFQ statistics"""
        try:
            total_rfqs = db.query(RFQ).count()
            
            # Count by status
            status_counts = db.query(
                RFQ.status,
                func.count(RFQ.id)
            ).group_by(RFQ.status).all()
            
            # Count by buyer
            buyer_counts = db.query(
                RFQ.buyer_id,
                func.count(RFQ.id)
            ).group_by(RFQ.buyer_id).all()
            
            # Average budget
            avg_budget = db.query(func.avg(RFQ.budget_range_max)).scalar()
            
            return {
                "total_rfqs": total_rfqs,
                "status_counts": dict(status_counts),
                "buyer_counts": dict(buyer_counts),
                "average_budget": float(avg_budget) if avg_budget else 0.0
            }
        except Exception as e:
            logger.error(f"Error getting RFQ stats: {e}")
            return {
                "total_rfqs": 0,
                "status_counts": {},
                "buyer_counts": {},
                "average_budget": 0.0
            }
    
    def _apply_search(self, query: Query, search_term: str) -> Query:
        """Apply search to RFQ query"""
        return query.filter(
            or_(
                RFQ.title.ilike(f"%{search_term}%"),
                RFQ.description.ilike(f"%{search_term}%"),
                RFQ.project_name.ilike(f"%{search_term}%")
            )
        ) 