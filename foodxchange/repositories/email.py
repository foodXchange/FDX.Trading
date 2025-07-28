from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc, func
from foodxchange.models.email import Email, EmailTask
from foodxchange.schemas.email import EmailCreate, EmailUpdate, EmailStatus, EmailClassification
from foodxchange.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class EmailRepository(BaseRepository[Email, EmailCreate, EmailUpdate]):
    """Repository for Email model with scheduling and analytics operations"""
    
    def __init__(self):
        super().__init__(Email)
    
    def get_by_recipient(self, db: Session, recipient_email: str, skip: int = 0, limit: int = 100) -> List[Email]:
        """Get emails by recipient"""
        try:
            return db.query(Email).filter(
                Email.to_emails.contains([recipient_email])
            ).order_by(desc(Email.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting emails by recipient {recipient_email}: {e}")
            return []
    
    def get_by_sender(self, db: Session, sender_email: str, skip: int = 0, limit: int = 100) -> List[Email]:
        """Get emails by sender"""
        try:
            return db.query(Email).filter(
                Email.from_email == sender_email
            ).order_by(desc(Email.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting emails by sender {sender_email}: {e}")
            return []
    
    def get_by_status(self, db: Session, status: EmailStatus, skip: int = 0, limit: int = 100) -> List[Email]:
        """Get emails by status"""
        try:
            return db.query(Email).filter(
                Email.status == status
            ).order_by(desc(Email.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting emails by status {status}: {e}")
            return []
    
    def get_by_classification(self, db: Session, classification: EmailClassification, skip: int = 0, limit: int = 100) -> List[Email]:
        """Get emails by classification"""
        try:
            return db.query(Email).filter(
                Email.classification == classification
            ).order_by(desc(Email.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting emails by classification {classification}: {e}")
            return []
    
    def get_scheduled_emails(self, db: Session, skip: int = 0, limit: int = 100) -> List[Email]:
        """Get scheduled emails"""
        try:
            from datetime import datetime
            return db.query(Email).filter(
                Email.scheduled_at.isnot(None),
                Email.scheduled_at > datetime.utcnow(),
                Email.status == EmailStatus.DRAFT
            ).order_by(Email.scheduled_at).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting scheduled emails: {e}")
            return []
    
    def get_pending_emails(self, db: Session, skip: int = 0, limit: int = 100) -> List[Email]:
        """Get pending emails (draft status)"""
        try:
            return db.query(Email).filter(
                Email.status == EmailStatus.DRAFT
            ).order_by(desc(Email.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting pending emails: {e}")
            return []
    
    def update_email_status(self, db: Session, email_id: int, status: EmailStatus, **kwargs) -> bool:
        """Update email status with optional timestamps"""
        try:
            email = self.get(db, email_id)
            if not email:
                return False
            
            email.status = status
            
            # Update timestamps based on status
            from datetime import datetime
            if status == EmailStatus.SENT and 'sent_at' in kwargs:
                email.sent_at = kwargs['sent_at']
            elif status == EmailStatus.DELIVERED and 'delivered_at' in kwargs:
                email.delivered_at = kwargs['delivered_at']
            elif status == EmailStatus.READ and 'read_at' in kwargs:
                email.read_at = kwargs['read_at']
            elif status == EmailStatus.FAILED and 'error_message' in kwargs:
                email.error_message = kwargs['error_message']
            
            db.add(email)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating status for email {email_id}: {e}")
            return False
    
    def get_email_tasks(self, db: Session, email_id: int) -> List[EmailTask]:
        """Get all tasks for an email"""
        try:
            return db.query(EmailTask).filter(
                EmailTask.email_id == email_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting tasks for email {email_id}: {e}")
            return []
    
    def get_email_analytics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get email analytics for the last N days"""
        try:
            from datetime import datetime, timedelta
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total counts
            total_sent = db.query(Email).filter(
                Email.sent_at >= start_date
            ).count()
            
            total_delivered = db.query(Email).filter(
                Email.delivered_at >= start_date
            ).count()
            
            total_read = db.query(Email).filter(
                Email.read_at >= start_date
            ).count()
            
            total_failed = db.query(Email).filter(
                Email.status == EmailStatus.FAILED,
                Email.created_at >= start_date
            ).count()
            
            # Calculate rates
            delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
            read_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0
            failure_rate = (total_failed / total_sent * 100) if total_sent > 0 else 0
            
            # Classification breakdown
            classification_counts = db.query(
                Email.classification,
                func.count(Email.id)
            ).filter(
                Email.created_at >= start_date
            ).group_by(Email.classification).all()
            
            # Status breakdown
            status_counts = db.query(
                Email.status,
                func.count(Email.id)
            ).filter(
                Email.created_at >= start_date
            ).group_by(Email.status).all()
            
            # Daily stats
            daily_stats = db.query(
                func.date(Email.created_at),
                func.count(Email.id)
            ).filter(
                Email.created_at >= start_date
            ).group_by(func.date(Email.created_at)).all()
            
            return {
                "period_days": days,
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "total_read": total_read,
                "total_failed": total_failed,
                "delivery_rate": round(delivery_rate, 2),
                "read_rate": round(read_rate, 2),
                "failure_rate": round(failure_rate, 2),
                "classification_breakdown": dict(classification_counts),
                "status_breakdown": dict(status_counts),
                "daily_stats": [{"date": str(date), "count": count} for date, count in daily_stats]
            }
        except Exception as e:
            logger.error(f"Error getting email analytics: {e}")
            return {
                "period_days": days,
                "total_sent": 0,
                "total_delivered": 0,
                "total_read": 0,
                "total_failed": 0,
                "delivery_rate": 0.0,
                "read_rate": 0.0,
                "failure_rate": 0.0,
                "classification_breakdown": {},
                "status_breakdown": {},
                "daily_stats": []
            }
    
    def get_email_stats(self, db: Session) -> Dict[str, Any]:
        """Get overall email statistics"""
        try:
            total_emails = db.query(Email).count()
            
            # Count by status
            status_counts = db.query(
                Email.status,
                func.count(Email.id)
            ).group_by(Email.status).all()
            
            # Count by classification
            classification_counts = db.query(
                Email.classification,
                func.count(Email.id)
            ).group_by(Email.classification).all()
            
            # Average priority
            avg_priority = db.query(func.avg(Email.priority)).scalar()
            
            return {
                "total_emails": total_emails,
                "status_counts": dict(status_counts),
                "classification_counts": dict(classification_counts),
                "average_priority": float(avg_priority) if avg_priority else 0.0
            }
        except Exception as e:
            logger.error(f"Error getting email stats: {e}")
            return {
                "total_emails": 0,
                "status_counts": {},
                "classification_counts": {},
                "average_priority": 0.0
            }
    
    def _apply_search(self, query: Query, search_term: str) -> Query:
        """Apply search to email query"""
        return query.filter(
            or_(
                Email.subject.ilike(f"%{search_term}%"),
                Email.body.ilike(f"%{search_term}%"),
                Email.from_email.ilike(f"%{search_term}%"),
                Email.to_emails.overlap([search_term])
            )
        ) 