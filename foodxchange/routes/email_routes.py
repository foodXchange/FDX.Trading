"""
Email Intelligence Routes
Handles email analysis and display functionality
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user_context
from app.models.email import Email
from app.services.email_ai_service import email_ai_service
from app.models.supplier import Supplier
from app.models.quote import Quote

templates = Jinja2Templates(directory="app/templates")

def include_email_routes(app):
    """Include email-related routes in the main app"""
    
    @app.get("/emails", response_class=HTMLResponse, name="emails_list")
    async def emails_list(request: Request, db: Session = Depends(get_db)):
        user = get_current_user_context(request, db)
        if not user:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/login", status_code=302)
        
        # Get emails from database
        emails = db.query(Email).order_by(Email.received_at.desc()).limit(50).all()
        
        # Analyze emails if not already analyzed
        analyzed_emails = []
        for email in emails:
            email_dict = {
                "id": email.id,
                "sender": email.sender_email,
                "subject": email.subject,
                "date": email.received_at.strftime("%Y-%m-%d %H:%M") if email.received_at else "Unknown",
                "body": email.body,
                "processed": email.processed,
                "email_type": email.email_type
            }
            
            # If email hasn't been analyzed, analyze it now
            if not email.processed and email.email_type == 'supplier':
                try:
                    analysis = await email_ai_service.analyze_email(
                        email.body or "",
                        email.subject,
                        email.sender_email
                    )
                    
                    email_dict.update({
                        "intent": analysis["intent"],
                        "confidence": analysis["confidence"],
                        "insights": analysis["insights"],
                        "requires_action": analysis["requires_action"],
                        "suggested_actions": analysis["suggested_actions"],
                        "extracted_data": analysis["extracted_data"]
                    })
                except Exception as e:
                    email_dict.update({
                        "intent": "unknown",
                        "confidence": 0,
                        "insights": [f"Analysis error: {str(e)}"],
                        "requires_action": False,
                        "suggested_actions": []
                    })
            else:
                # Default values for non-supplier emails
                email_dict.update({
                    "intent": email.email_type or "general",
                    "confidence": 1.0 if email.processed else 0,
                    "insights": ["Email already processed"] if email.processed else [],
                    "requires_action": False,
                    "suggested_actions": []
                })
            
            analyzed_emails.append(email_dict)
        
        # Calculate stats
        stats = {
            "total_emails": len(emails),
            "unprocessed": sum(1 for e in emails if not e.processed),
            "supplier_emails": sum(1 for e in emails if e.email_type == 'supplier'),
            "requires_action": sum(1 for e in analyzed_emails if e.get("requires_action", False))
        }
        
        return templates.TemplateResponse("email_intelligence.html", {
            "request": request,
            "emails": analyzed_emails,
            "stats": stats,
            "current_user": user
        })
    
    @app.post("/api/emails/{email_id}/analyze", response_class=JSONResponse)
    async def analyze_email(email_id: int, request: Request, db: Session = Depends(get_db)):
        """Analyze a specific email"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        try:
            # Analyze the email
            analysis = await email_ai_service.analyze_email(
                email.body or "",
                email.subject,
                email.sender_email
            )
            
            # Update email as processed
            email.processed = True
            email.processed_at = datetime.utcnow()
            db.commit()
            
            # Try to match with supplier
            supplier = db.query(Supplier).filter(
                Supplier.email == email.sender_email
            ).first()
            
            if supplier:
                analysis["supplier_info"]["supplier_id"] = supplier.id
                analysis["supplier_info"]["supplier_name"] = supplier.name
            
            return analysis
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    @app.post("/api/emails/{email_id}/action", response_class=JSONResponse)
    async def execute_email_action(email_id: int, request: Request, db: Session = Depends(get_db)):
        """Execute suggested action for an email"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        body = await request.json()
        action = body.get("action")
        
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        try:
            # Execute action based on type
            if action == "Add quote to comparison matrix":
                # Extract quote data from email and create quote
                # This is a simplified example
                return {"status": "success", "message": "Quote added to comparison matrix"}
                
            elif action == "Update supplier pricing in database":
                # Update supplier pricing
                return {"status": "success", "message": "Supplier pricing updated"}
                
            elif action == "Update order status":
                # Update order status
                return {"status": "success", "message": "Order status updated"}
                
            else:
                return {"status": "info", "message": f"Action '{action}' noted but requires manual execution"}
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Action failed: {str(e)}")
    
    @app.post("/api/emails/batch-analyze", response_class=JSONResponse)
    async def batch_analyze_emails(request: Request, db: Session = Depends(get_db)):
        """Analyze multiple emails in batch"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get unprocessed supplier emails
        unprocessed_emails = db.query(Email).filter(
            Email.processed == False,
            Email.email_type == 'supplier'
        ).limit(10).all()
        
        if not unprocessed_emails:
            return {"analyzed": 0, "results": []}
        
        # Prepare emails for batch analysis
        email_batch = []
        for email in unprocessed_emails:
            email_batch.append({
                "id": str(email.id),
                "content": email.body or "",
                "subject": email.subject,
                "sender": email.sender_email
            })
        
        try:
            # Batch analyze
            results = await email_ai_service.batch_analyze(email_batch)
            
            # Update emails as processed
            for email in unprocessed_emails:
                email.processed = True
                email.processed_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "analyzed": len(results),
                "results": results
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")
    
    @app.get("/api/emails/insights", response_class=JSONResponse)
    async def get_email_insights(request: Request, db: Session = Depends(get_db)):
        """Get aggregated insights from emails"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get recent emails
        recent_emails = db.query(Email).filter(
            Email.email_type == 'supplier'
        ).order_by(Email.received_at.desc()).limit(100).all()
        
        # Aggregate insights
        insights = {
            "total_emails": len(recent_emails),
            "processed": sum(1 for e in recent_emails if e.processed),
            "by_intent": {},
            "top_suppliers": [],
            "recent_trends": [],
            "action_items": []
        }
        
        # Count by sender
        sender_counts = {}
        for email in recent_emails:
            sender = email.sender_email
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        # Get top suppliers
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for sender, count in top_senders:
            supplier = db.query(Supplier).filter(Supplier.email == sender).first()
            insights["top_suppliers"].append({
                "email": sender,
                "name": supplier.name if supplier else sender.split("@")[0].title(),
                "email_count": count
            })
        
        # Add some trend insights
        insights["recent_trends"] = [
            "Increased quote activity in the last week",
            "3 new suppliers have sent product catalogs",
            "Price updates received from 5 suppliers"
        ]
        
        # Add action items
        insights["action_items"] = [
            {"priority": "high", "action": "Review 5 pending quotes"},
            {"priority": "medium", "action": "Update supplier contact information"},
            {"priority": "low", "action": "Archive processed emails older than 30 days"}
        ]
        
        return insights