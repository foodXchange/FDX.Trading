"""
Support System Service
Handles ticket management, error categorization, and support analytics
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from fastapi import HTTPException

from foodxchange.models.support import (
    SupportTicket, TicketStatusHistory, TicketResponse, ErrorLog,
    SupportAnalytics, UserFeedback, TicketStatus, TicketPriority,
    TicketCategory, ErrorSeverity
)
from foodxchange.models.user import User

logger = logging.getLogger(__name__)


class SupportService:
    """Main support service for ticket management and analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_ticket_id(self) -> str:
        """Generate unique ticket ID"""
        return f"TKT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    def create_ticket(
        self,
        db: Session,
        user_id: int,
        title: str,
        description: str,
        category: TicketCategory,
        priority: TicketPriority = TicketPriority.MEDIUM,
        error_id: Optional[str] = None,
        browser_info: Optional[Dict] = None,
        device_info: Optional[Dict] = None,
        steps_to_reproduce: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        actual_behavior: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> SupportTicket:
        """Create a new support ticket"""
        try:
            ticket = SupportTicket(
                ticket_id=self.generate_ticket_id(),
                user_id=user_id,
                title=title,
                description=description,
                category=category,
                priority=priority,
                error_id=error_id,
                browser_info=browser_info,
                device_info=device_info,
                steps_to_reproduce=steps_to_reproduce,
                expected_behavior=expected_behavior,
                actual_behavior=actual_behavior,
                attachments=attachments or []
            )
            
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            
            # Create initial status history
            status_history = TicketStatusHistory(
                ticket_id=ticket.id,
                status=TicketStatus.NEW,
                changed_by=user_id,
                notes="Ticket created"
            )
            db.add(status_history)
            db.commit()
            
            self.logger.info(f"Created support ticket {ticket.ticket_id} for user {user_id}")
            return ticket
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating support ticket: {e}")
            raise HTTPException(status_code=500, detail="Failed to create support ticket")
    
    def get_ticket(self, db: Session, ticket_id: str) -> Optional[SupportTicket]:
        """Get ticket by ticket ID"""
        return db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
    
    def get_user_tickets(
        self,
        db: Session,
        user_id: int,
        status: Optional[TicketStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[SupportTicket], int]:
        """Get tickets for a user with optional filtering"""
        query = db.query(SupportTicket).filter(SupportTicket.user_id == user_id)
        
        if status:
            query = query.filter(SupportTicket.status == status)
        
        total = query.count()
        tickets = query.order_by(desc(SupportTicket.created_at)).offset(offset).limit(limit).all()
        
        return tickets, total
    
    def get_all_tickets(
        self,
        db: Session,
        status: Optional[TicketStatus] = None,
        category: Optional[TicketCategory] = None,
        priority: Optional[TicketPriority] = None,
        assigned_to: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[SupportTicket], int]:
        """Get all tickets with filtering options"""
        query = db.query(SupportTicket)
        
        if status:
            query = query.filter(SupportTicket.status == status)
        if category:
            query = query.filter(SupportTicket.category == category)
        if priority:
            query = query.filter(SupportTicket.priority == priority)
        if assigned_to:
            query = query.filter(SupportTicket.assigned_to == assigned_to)
        
        total = query.count()
        tickets = query.order_by(desc(SupportTicket.created_at)).offset(offset).limit(limit).all()
        
        return tickets, total
    
    def update_ticket_status(
        self,
        db: Session,
        ticket_id: str,
        new_status: TicketStatus,
        changed_by: int,
        notes: Optional[str] = None
    ) -> SupportTicket:
        """Update ticket status and create history record"""
        ticket = self.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()
        
        # Set resolved_at if status is resolved
        if new_status == TicketStatus.RESOLVED and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
        
        # Set closed_at if status is closed
        if new_status == TicketStatus.CLOSED and not ticket.closed_at:
            ticket.closed_at = datetime.utcnow()
        
        # Create status history record
        status_history = TicketStatusHistory(
            ticket_id=ticket.id,
            status=new_status,
            changed_by=changed_by,
            notes=notes or f"Status changed from {old_status.value} to {new_status.value}"
        )
        
        db.add(status_history)
        db.commit()
        db.refresh(ticket)
        
        self.logger.info(f"Updated ticket {ticket_id} status from {old_status.value} to {new_status.value}")
        return ticket
    
    def assign_ticket(
        self,
        db: Session,
        ticket_id: str,
        assigned_to: int,
        assigned_by: int
    ) -> SupportTicket:
        """Assign ticket to a user"""
        ticket = self.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        ticket.assigned_to = assigned_to
        ticket.updated_at = datetime.utcnow()
        
        # Create status history record
        status_history = TicketStatusHistory(
            ticket_id=ticket.id,
            status=ticket.status,
            changed_by=assigned_by,
            notes=f"Ticket assigned to user {assigned_to}"
        )
        
        db.add(status_history)
        db.commit()
        db.refresh(ticket)
        
        self.logger.info(f"Assigned ticket {ticket_id} to user {assigned_to}")
        return ticket
    
    def add_ticket_response(
        self,
        db: Session,
        ticket_id: str,
        user_id: int,
        message: str,
        is_internal: bool = False,
        attachments: Optional[List[str]] = None
    ) -> TicketResponse:
        """Add a response to a ticket"""
        ticket = self.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        response = TicketResponse(
            ticket_id=ticket.id,
            user_id=user_id,
            message=message,
            is_internal=is_internal,
            attachments=attachments or []
        )
        
        db.add(response)
        db.commit()
        db.refresh(response)
        
        self.logger.info(f"Added response to ticket {ticket_id} by user {user_id}")
        return response
    
    def log_error(
        self,
        db: Session,
        error_id: str,
        error_type: str,
        error_message: str,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: Optional[TicketCategory] = None,
        url_path: Optional[str] = None,
        http_method: Optional[str] = None,
        status_code: Optional[int] = None,
        browser_info: Optional[Dict] = None,
        device_info: Optional[Dict] = None,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
        context_data: Optional[Dict] = None
    ) -> ErrorLog:
        """Log an error with support integration"""
        try:
            error_log = ErrorLog(
                error_id=error_id,
                request_id=request_id,
                user_id=user_id,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                severity=severity,
                category=category,
                url_path=url_path,
                http_method=http_method,
                status_code=status_code,
                browser_info=browser_info,
                device_info=device_info,
                request_data=request_data,
                response_data=response_data,
                context_data=context_data
            )
            
            db.add(error_log)
            db.commit()
            db.refresh(error_log)
            
            self.logger.info(f"Logged error {error_id} with severity {severity.value}")
            return error_log
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error logging error: {e}")
            raise
    
    def get_error_logs(
        self,
        db: Session,
        user_id: Optional[int] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[TicketCategory] = None,
        resolved: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[ErrorLog], int]:
        """Get error logs with filtering"""
        query = db.query(ErrorLog)
        
        if user_id:
            query = query.filter(ErrorLog.user_id == user_id)
        if severity:
            query = query.filter(ErrorLog.severity == severity)
        if category:
            query = query.filter(ErrorLog.category == category)
        if resolved is not None:
            query = query.filter(ErrorLog.resolved == resolved)
        
        total = query.count()
        logs = query.order_by(desc(ErrorLog.created_at)).offset(offset).limit(limit).all()
        
        return logs, total
    
    def resolve_error(
        self,
        db: Session,
        error_id: str,
        resolved_by: int,
        ticket_id: Optional[int] = None
    ) -> ErrorLog:
        """Mark an error as resolved"""
        error_log = db.query(ErrorLog).filter(ErrorLog.error_id == error_id).first()
        if not error_log:
            raise HTTPException(status_code=404, detail="Error log not found")
        
        error_log.resolved = True
        error_log.resolved_at = datetime.utcnow()
        error_log.resolved_by = resolved_by
        if ticket_id:
            error_log.ticket_id = ticket_id
        
        db.commit()
        db.refresh(error_log)
        
        self.logger.info(f"Resolved error {error_id}")
        return error_log
    
    def create_user_feedback(
        self,
        db: Session,
        feedback_type: str,
        title: str,
        description: str,
        user_id: Optional[int] = None,
        category: Optional[TicketCategory] = None,
        priority: TicketPriority = TicketPriority.MEDIUM,
        browser_info: Optional[Dict] = None,
        device_info: Optional[Dict] = None,
        screenshots: Optional[List[str]] = None,
        contact_email: Optional[str] = None
    ) -> UserFeedback:
        """Create user feedback or bug report"""
        try:
            feedback = UserFeedback(
                user_id=user_id,
                feedback_type=feedback_type,
                title=title,
                description=description,
                category=category,
                priority=priority,
                browser_info=browser_info,
                device_info=device_info,
                screenshots=screenshots or [],
                contact_email=contact_email
            )
            
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            
            self.logger.info(f"Created user feedback {feedback.id} of type {feedback_type}")
            return feedback
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating user feedback: {e}")
            raise HTTPException(status_code=500, detail="Failed to create feedback")
    
    def get_support_analytics(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get support system analytics for the specified period"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Ticket analytics
        tickets_query = db.query(SupportTicket).filter(
            SupportTicket.created_at >= start_date
        )
        
        total_tickets = tickets_query.count()
        new_tickets = tickets_query.filter(SupportTicket.status == TicketStatus.NEW).count()
        resolved_tickets = tickets_query.filter(SupportTicket.status == TicketStatus.RESOLVED).count()
        
        # Calculate average resolution time
        resolved_tickets_with_time = db.query(SupportTicket).filter(
            and_(
                SupportTicket.created_at >= start_date,
                SupportTicket.status == TicketStatus.RESOLVED,
                SupportTicket.resolved_at.isnot(None)
            )
        ).all()
        
        total_resolution_time = 0
        for ticket in resolved_tickets_with_time:
            if ticket.resolved_at:
                resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600  # hours
                total_resolution_time += resolution_time
        
        avg_resolution_time = total_resolution_time / len(resolved_tickets_with_time) if resolved_tickets_with_time else 0
        
        # Tickets by category
        tickets_by_category = db.query(
            SupportTicket.category,
            func.count(SupportTicket.id)
        ).filter(
            SupportTicket.created_at >= start_date
        ).group_by(SupportTicket.category).all()
        
        # Tickets by priority
        tickets_by_priority = db.query(
            SupportTicket.priority,
            func.count(SupportTicket.id)
        ).filter(
            SupportTicket.created_at >= start_date
        ).group_by(SupportTicket.priority).all()
        
        # Error analytics
        errors_query = db.query(ErrorLog).filter(ErrorLog.created_at >= start_date)
        error_count = errors_query.count()
        critical_errors = errors_query.filter(ErrorLog.severity == ErrorSeverity.CRITICAL).count()
        
        return {
            "period_days": days,
            "total_tickets": total_tickets,
            "new_tickets": new_tickets,
            "resolved_tickets": resolved_tickets,
            "avg_resolution_time_hours": round(avg_resolution_time, 2),
            "tickets_by_category": {cat.value: count for cat, count in tickets_by_category},
            "tickets_by_priority": {pri.value: count for pri, count in tickets_by_priority},
            "error_count": error_count,
            "critical_errors": critical_errors,
            "resolution_rate": (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
        }
    
    def save_daily_analytics(self, db: Session) -> SupportAnalytics:
        """Save daily analytics snapshot"""
        analytics_data = self.get_support_analytics(db, days=1)
        
        analytics = SupportAnalytics(
            date=datetime.utcnow().date(),
            total_tickets=analytics_data["total_tickets"],
            new_tickets=analytics_data["new_tickets"],
            resolved_tickets=analytics_data["resolved_tickets"],
            avg_resolution_time=analytics_data["avg_resolution_time_hours"],
            tickets_by_category=analytics_data["tickets_by_category"],
            tickets_by_priority=analytics_data["tickets_by_priority"],
            error_count=analytics_data["error_count"],
            critical_errors=analytics_data["critical_errors"]
        )
        
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        
        return analytics


# Global instance
support_service = SupportService() 