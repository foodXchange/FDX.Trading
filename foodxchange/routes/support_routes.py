"""
Support System API Routes
Provides endpoints for ticket management, user feedback, and support analytics
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Query, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime

from foodxchange.services.support_service import support_service
from foodxchange.models.support import (
    TicketStatus, TicketPriority, TicketCategory, ErrorSeverity
)
from foodxchange.database import get_db
from sqlalchemy.orm import Session

# Mock user for now - replace with actual auth
class User:
    id: int = 1
    email: str = "admin@foodxchange.com"
    is_admin: bool = True

def get_current_user():
    """Mock function to avoid circular import"""
    return User()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support", tags=["Support System"])


# Pydantic models for API requests/responses
class CreateTicketRequest(BaseModel):
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    error_id: Optional[str] = None
    browser_info: Optional[Dict] = None
    device_info: Optional[Dict] = None
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None


class UpdateTicketRequest(BaseModel):
    status: Optional[TicketStatus] = None
    assigned_to: Optional[int] = None
    priority: Optional[TicketPriority] = None


class TicketResponseRequest(BaseModel):
    message: str
    is_internal: bool = False
    attachments: Optional[List[str]] = None


class UserFeedbackRequest(BaseModel):
    feedback_type: str  # bug_report, feature_request, general
    title: str
    description: str
    category: Optional[TicketCategory] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    browser_info: Optional[Dict] = None
    device_info: Optional[Dict] = None
    screenshots: Optional[List[str]] = None
    contact_email: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    ticket_id: str
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    assigned_to: Optional[int]
    error_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    user: Dict[str, Any]
    assignee: Optional[Dict[str, Any]]


class TicketDetailResponse(TicketResponse):
    browser_info: Optional[Dict]
    device_info: Optional[Dict]
    steps_to_reproduce: Optional[str]
    expected_behavior: Optional[str]
    actual_behavior: Optional[str]
    attachments: List[str]
    status_history: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]


# Public Support Endpoints
@router.post("/tickets", response_model=Dict[str, Any])
async def create_support_ticket(
    request: CreateTicketRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new support ticket"""
    try:
        ticket = support_service.create_ticket(
            db=db,
            user_id=current_user.id,
            title=request.title,
            description=request.description,
            category=request.category,
            priority=request.priority,
            error_id=request.error_id,
            browser_info=request.browser_info,
            device_info=request.device_info,
            steps_to_reproduce=request.steps_to_reproduce,
            expected_behavior=request.expected_behavior,
            actual_behavior=request.actual_behavior
        )
        
        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "message": "Support ticket created successfully",
            "ticket": {
                "id": ticket.id,
                "ticket_id": ticket.ticket_id,
                "title": ticket.title,
                "status": ticket.status.value,
                "priority": ticket.priority.value,
                "category": ticket.category.value,
                "created_at": ticket.created_at.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error creating support ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to create support ticket")


@router.get("/tickets", response_model=Dict[str, Any])
async def get_user_tickets(
    status: Optional[TicketStatus] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tickets for the current user"""
    try:
        tickets, total = support_service.get_user_tickets(
            db=db,
            user_id=current_user.id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "tickets": [
                {
                    "id": ticket.id,
                    "ticket_id": ticket.ticket_id,
                    "title": ticket.title,
                    "description": ticket.description,
                    "category": ticket.category.value,
                    "priority": ticket.priority.value,
                    "status": ticket.status.value,
                    "assigned_to": ticket.assigned_to,
                    "created_at": ticket.created_at.isoformat(),
                    "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                    "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None
                }
                for ticket in tickets
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting user tickets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tickets")


@router.get("/tickets/{ticket_id}", response_model=Dict[str, Any])
async def get_ticket_details(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific ticket"""
    try:
        ticket = support_service.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Check if user has access to this ticket
        if ticket.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "ticket": {
                "id": ticket.id,
                "ticket_id": ticket.ticket_id,
                "title": ticket.title,
                "description": ticket.description,
                "category": ticket.category.value,
                "priority": ticket.priority.value,
                "status": ticket.status.value,
                "assigned_to": ticket.assigned_to,
                "error_id": ticket.error_id,
                "browser_info": ticket.browser_info,
                "device_info": ticket.device_info,
                "steps_to_reproduce": ticket.steps_to_reproduce,
                "expected_behavior": ticket.expected_behavior,
                "actual_behavior": ticket.actual_behavior,
                "attachments": ticket.attachments,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None,
                "status_history": [
                    {
                        "status": history.status.value,
                        "changed_by": history.changed_by,
                        "notes": history.notes,
                        "created_at": history.created_at.isoformat()
                    }
                    for history in ticket.status_history
                ],
                "responses": [
                    {
                        "id": response.id,
                        "user_id": response.user_id,
                        "message": response.message,
                        "is_internal": response.is_internal,
                        "attachments": response.attachments,
                        "created_at": response.created_at.isoformat()
                    }
                    for response in ticket.responses
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ticket details")


@router.post("/tickets/{ticket_id}/responses", response_model=Dict[str, Any])
async def add_ticket_response(
    ticket_id: str,
    request: TicketResponseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a response to a ticket"""
    try:
        ticket = support_service.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Check if user has access to this ticket
        if ticket.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        response = support_service.add_ticket_response(
            db=db,
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=request.message,
            is_internal=request.is_internal,
            attachments=request.attachments
        )
        
        return {
            "success": True,
            "response_id": response.id,
            "message": "Response added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding ticket response: {e}")
        raise HTTPException(status_code=500, detail="Failed to add response")


@router.post("/feedback", response_model=Dict[str, Any])
async def submit_user_feedback(
    request: UserFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit user feedback or bug report"""
    try:
        feedback = support_service.create_user_feedback(
            db=db,
            feedback_type=request.feedback_type,
            title=request.title,
            description=request.description,
            user_id=current_user.id,
            category=request.category,
            priority=request.priority,
            browser_info=request.browser_info,
            device_info=request.device_info,
            screenshots=request.screenshots,
            contact_email=request.contact_email
        )
        
        return {
            "success": True,
            "feedback_id": feedback.id,
            "message": "Feedback submitted successfully"
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/categories", response_model=Dict[str, Any])
async def get_support_categories():
    """Get available support categories"""
    return {
        "success": True,
        "categories": [
            {"value": cat.value, "label": cat.value.replace("_", " ").title()}
            for cat in TicketCategory
        ]
    }


@router.get("/priorities", response_model=Dict[str, Any])
async def get_support_priorities():
    """Get available support priorities"""
    return {
        "success": True,
        "priorities": [
            {"value": pri.value, "label": pri.value.title()}
            for pri in TicketPriority
        ]
    }


@router.get("/statuses", response_model=Dict[str, Any])
async def get_support_statuses():
    """Get available support statuses"""
    return {
        "success": True,
        "statuses": [
            {"value": status.value, "label": status.value.replace("_", " ").title()}
            for status in TicketStatus
        ]
    }


# Admin Support Endpoints
@router.get("/admin/tickets", response_model=Dict[str, Any])
async def get_all_tickets_admin(
    status: Optional[TicketStatus] = Query(None),
    category: Optional[TicketCategory] = Query(None),
    priority: Optional[TicketPriority] = Query(None),
    assigned_to: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tickets (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        tickets, total = support_service.get_all_tickets(
            db=db,
            status=status,
            category=category,
            priority=priority,
            assigned_to=assigned_to,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "tickets": [
                {
                    "id": ticket.id,
                    "ticket_id": ticket.ticket_id,
                    "title": ticket.title,
                    "description": ticket.description,
                    "category": ticket.category.value,
                    "priority": ticket.priority.value,
                    "status": ticket.status.value,
                    "assigned_to": ticket.assigned_to,
                    "user_id": ticket.user_id,
                    "created_at": ticket.created_at.isoformat(),
                    "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                    "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None
                }
                for ticket in tickets
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting all tickets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tickets")


@router.put("/admin/tickets/{ticket_id}/status", response_model=Dict[str, Any])
async def update_ticket_status_admin(
    ticket_id: str,
    status: TicketStatus,
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update ticket status (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        ticket = support_service.update_ticket_status(
            db=db,
            ticket_id=ticket_id,
            new_status=status,
            changed_by=current_user.id,
            notes=notes
        )
        
        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "status": ticket.status.value,
            "message": "Ticket status updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update ticket status")


@router.put("/admin/tickets/{ticket_id}/assign", response_model=Dict[str, Any])
async def assign_ticket_admin(
    ticket_id: str,
    assigned_to: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign ticket to a user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        ticket = support_service.assign_ticket(
            db=db,
            ticket_id=ticket_id,
            assigned_to=assigned_to,
            assigned_by=current_user.id
        )
        
        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "assigned_to": ticket.assigned_to,
            "message": "Ticket assigned successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign ticket")


@router.get("/admin/analytics", response_model=Dict[str, Any])
async def get_support_analytics_admin(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get support analytics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        analytics = support_service.get_support_analytics(db, days=days)
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")


@router.get("/admin/errors", response_model=Dict[str, Any])
async def get_error_logs_admin(
    severity: Optional[ErrorSeverity] = Query(None),
    category: Optional[TicketCategory] = Query(None),
    resolved: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get error logs (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        logs, total = support_service.get_error_logs(
            db=db,
            severity=severity,
            category=category,
            resolved=resolved,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "logs": [
                {
                    "id": log.id,
                    "error_id": log.error_id,
                    "request_id": log.request_id,
                    "user_id": log.user_id,
                    "error_type": log.error_type,
                    "error_message": log.error_message,
                    "severity": log.severity.value,
                    "category": log.category.value if log.category else None,
                    "url_path": log.url_path,
                    "http_method": log.http_method,
                    "status_code": log.status_code,
                    "resolved": log.resolved,
                    "created_at": log.created_at.isoformat(),
                    "resolved_at": log.resolved_at.isoformat() if log.resolved_at else None
                }
                for log in logs
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting error logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get error logs")


@router.put("/admin/errors/{error_id}/resolve", response_model=Dict[str, Any])
async def resolve_error_admin(
    error_id: str,
    ticket_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark error as resolved (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        error_log = support_service.resolve_error(
            db=db,
            error_id=error_id,
            resolved_by=current_user.id,
            ticket_id=ticket_id
        )
        
        return {
            "success": True,
            "error_id": error_log.error_id,
            "message": "Error marked as resolved"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve error")


# Support Center Page
@router.get("/center", response_class=HTMLResponse)
async def support_center_page():
    """Support center page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Support Center - FoodXchange</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col-12">
                    <h1 class="text-center mb-5">
                        <i class="fas fa-headset text-primary"></i>
                        Support Center
                    </h1>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-ticket-alt fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Create Support Ticket</h5>
                            <p class="card-text">Report an issue or request assistance with our platform.</p>
                            <button class="btn btn-primary" onclick="showTicketForm()">
                                Create Ticket
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-bug fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Report Bug</h5>
                            <p class="card-text">Found a bug? Help us improve by reporting it.</p>
                            <button class="btn btn-warning" onclick="showBugReportForm()">
                                Report Bug
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-lightbulb fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Feature Request</h5>
                            <p class="card-text">Have an idea for a new feature? Let us know!</p>
                            <button class="btn btn-success" onclick="showFeatureRequestForm()">
                                Request Feature
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-list"></i> My Support Tickets</h5>
                        </div>
                        <div class="card-body">
                            <div id="ticketsList">
                                <div class="text-center">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Load tickets on page load
            document.addEventListener('DOMContentLoaded', function() {
                loadUserTickets();
            });
            
            function loadUserTickets() {
                fetch('/api/support/tickets')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            displayTickets(data.tickets);
                        } else {
                            document.getElementById('ticketsList').innerHTML = 
                                '<div class="alert alert-danger">Failed to load tickets</div>';
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        document.getElementById('ticketsList').innerHTML = 
                            '<div class="alert alert-danger">Error loading tickets</div>';
                    });
            }
            
            function displayTickets(tickets) {
                const container = document.getElementById('ticketsList');
                
                if (tickets.length === 0) {
                    container.innerHTML = '<p class="text-muted text-center">No tickets found.</p>';
                    return;
                }
                
                const html = tickets.map(ticket => `
                    <div class="card mb-3">
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6 class="card-title">${ticket.title}</h6>
                                    <p class="card-text text-muted">${ticket.description.substring(0, 100)}...</p>
                                </div>
                                <div class="col-md-4 text-end">
                                    <span class="badge bg-${getStatusColor(ticket.status)}">${ticket.status}</span>
                                    <span class="badge bg-${getPriorityColor(ticket.priority)}">${ticket.priority}</span>
                                    <br>
                                    <small class="text-muted">${new Date(ticket.created_at).toLocaleDateString()}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                container.innerHTML = html;
            }
            
            function getStatusColor(status) {
                const colors = {
                    'new': 'primary',
                    'acknowledged': 'info',
                    'investigating': 'warning',
                    'in_progress': 'warning',
                    'testing': 'info',
                    'resolved': 'success',
                    'closed': 'secondary'
                };
                return colors[status] || 'secondary';
            }
            
            function getPriorityColor(priority) {
                const colors = {
                    'low': 'success',
                    'medium': 'warning',
                    'high': 'danger',
                    'critical': 'danger'
                };
                return colors[priority] || 'secondary';
            }
            
            function showTicketForm() {
                // Implementation for ticket form modal
                alert('Ticket form will be implemented here');
            }
            
            function showBugReportForm() {
                // Implementation for bug report form
                alert('Bug report form will be implemented here');
            }
            
            function showFeatureRequestForm() {
                // Implementation for feature request form
                alert('Feature request form will be implemented here');
            }
        </script>
    </body>
    </html>
    """ 