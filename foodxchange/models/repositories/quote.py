from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc, func
from foodxchange.models.quote import Quote, QuoteItem
from foodxchange.schemas.quote import QuoteCreate, QuoteUpdate, QuoteStatus
from foodxchange.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class QuoteRepository(BaseRepository[Quote, QuoteCreate, QuoteUpdate]):
    """Repository for Quote model with comparison and evaluation operations"""
    
    def __init__(self):
        super().__init__(Quote)
    
    def get_by_rfq(self, db: Session, rfq_id: int, skip: int = 0, limit: int = 100) -> List[Quote]:
        """Get quotes by RFQ"""
        try:
            return db.query(Quote).filter(
                Quote.rfq_id == rfq_id
            ).order_by(Quote.total_amount).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting quotes by RFQ {rfq_id}: {e}")
            return []
    
    def get_by_supplier(self, db: Session, supplier_id: int, skip: int = 0, limit: int = 100) -> List[Quote]:
        """Get quotes by supplier"""
        try:
            return db.query(Quote).filter(
                Quote.supplier_id == supplier_id
            ).order_by(desc(Quote.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting quotes by supplier {supplier_id}: {e}")
            return []
    
    def get_by_status(self, db: Session, status: QuoteStatus, skip: int = 0, limit: int = 100) -> List[Quote]:
        """Get quotes by status"""
        try:
            return db.query(Quote).filter(
                Quote.status == status
            ).order_by(desc(Quote.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting quotes by status {status}: {e}")
            return []
    
    def get_quote_with_details(self, db: Session, quote_id: int) -> Optional[Quote]:
        """Get quote with all related details"""
        try:
            return db.query(Quote).options(
                db.joinedload(Quote.items)
            ).filter(Quote.id == quote_id).first()
        except Exception as e:
            logger.error(f"Error getting quote details for {quote_id}: {e}")
            return None
    
    def get_quote_comparison(self, db: Session, rfq_id: int) -> Dict[str, Any]:
        """Get quote comparison for an RFQ"""
        try:
            quotes = self.get_by_rfq(db, rfq_id)
            
            if not quotes:
                return {"quotes": [], "comparison": {}}
            
            # Calculate comparison metrics
            total_amounts = [q.total_amount for q in quotes]
            min_amount = min(total_amounts)
            max_amount = max(total_amounts)
            avg_amount = sum(total_amounts) / len(total_amounts)
            
            # Find best quote (lowest amount)
            best_quote = min(quotes, key=lambda q: q.total_amount)
            
            # Calculate price differences
            price_differences = []
            for quote in quotes:
                diff = ((quote.total_amount - min_amount) / min_amount) * 100 if min_amount > 0 else 0
                price_differences.append({
                    "quote_id": quote.id,
                    "supplier_name": quote.supplier.company_name if quote.supplier else "Unknown",
                    "amount": quote.total_amount,
                    "difference_percent": round(diff, 2)
                })
            
            comparison = {
                "total_quotes": len(quotes),
                "min_amount": min_amount,
                "max_amount": max_amount,
                "avg_amount": round(avg_amount, 2),
                "best_quote_id": best_quote.id,
                "price_differences": price_differences
            }
            
            return {
                "quotes": quotes,
                "comparison": comparison
            }
        except Exception as e:
            logger.error(f"Error getting quote comparison for RFQ {rfq_id}: {e}")
            return {"quotes": [], "comparison": {}}
    
    def update_evaluation(self, db: Session, quote_id: int, score: float, notes: str) -> bool:
        """Update quote evaluation"""
        try:
            quote = self.get(db, quote_id)
            if not quote:
                return False
            
            quote.evaluation_score = score
            quote.evaluation_notes = notes
            db.add(quote)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating evaluation for quote {quote_id}: {e}")
            return False
    
    def get_quote_items(self, db: Session, quote_id: int) -> List[QuoteItem]:
        """Get all items for a quote"""
        try:
            return db.query(QuoteItem).filter(
                QuoteItem.quote_id == quote_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting items for quote {quote_id}: {e}")
            return []
    
    def get_quote_stats(self, db: Session) -> Dict[str, Any]:
        """Get quote statistics"""
        try:
            total_quotes = db.query(Quote).count()
            
            # Count by status
            status_counts = db.query(
                Quote.status,
                func.count(Quote.id)
            ).group_by(Quote.status).all()
            
            # Average quote amount
            avg_amount = db.query(func.avg(Quote.total_amount)).scalar()
            
            # Average evaluation score
            avg_score = db.query(func.avg(Quote.evaluation_score)).scalar()
            
            return {
                "total_quotes": total_quotes,
                "status_counts": dict(status_counts),
                "average_amount": float(avg_amount) if avg_amount else 0.0,
                "average_evaluation_score": float(avg_score) if avg_score else 0.0
            }
        except Exception as e:
            logger.error(f"Error getting quote stats: {e}")
            return {
                "total_quotes": 0,
                "status_counts": {},
                "average_amount": 0.0,
                "average_evaluation_score": 0.0
            }
    
    def get_best_quotes(self, db: Session, rfq_id: int, limit: int = 5) -> List[Quote]:
        """Get best quotes for an RFQ (lowest amount)"""
        try:
            return db.query(Quote).filter(
                Quote.rfq_id == rfq_id
            ).order_by(Quote.total_amount).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting best quotes for RFQ {rfq_id}: {e}")
            return []
    
    def _apply_search(self, query: Query, search_term: str) -> Query:
        """Apply search to quote query"""
        return query.filter(
            or_(
                Quote.additional_notes.ilike(f"%{search_term}%"),
                Quote.payment_terms.ilike(f"%{search_term}%"),
                Quote.delivery_terms.ilike(f"%{search_term}%")
            )
        ) 