"""
Email CRM Routes for FastAPI
Simple, lean interface with Bootstrap
"""

from fastapi import APIRouter, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.email_crm.service import email_crm
from app.email_crm.tracker import EmailTracker
import os

router = APIRouter(prefix="/email", tags=["email"])

def get_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

@router.get("/", response_class=HTMLResponse)
async def email_dashboard(request: Request):
    """Simple email dashboard"""
    # Get stats
    stats = email_crm.get_email_stats(7)
    
    # Get recent emails
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT e.*, s.supplier_name, s.country
        FROM email_log e
        LEFT JOIN suppliers s ON e.supplier_id = s.id
        ORDER BY e.sent_at DESC
        LIMIT 20
    """)
    recent = cur.fetchall()
    
    # Get pipeline counts
    cur.execute("""
        SELECT 
            COUNT(DISTINCT s.id) as total_suppliers,
            COUNT(DISTINCT CASE WHEN e.id IS NOT NULL THEN s.id END) as contacted,
            COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN s.id END) as opened,
            COUNT(DISTINCT CASE WHEN r.interested = true THEN s.id END) as interested
        FROM suppliers s
        LEFT JOIN email_log e ON s.id = e.supplier_id
        LEFT JOIN email_responses r ON r.from_email = s.company_email
    """)
    pipeline = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return request.app.state.templates.TemplateResponse("email/dashboard.html", {
        "request": request,
        "stats": stats,
        "recent": recent,
        "pipeline": pipeline
    })

@router.get("/compose", response_class=HTMLResponse)
async def compose_email(request: Request):
    """Email composer page"""
    # Get suppliers for dropdown
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT id, supplier_name, company_email, country 
        FROM suppliers 
        WHERE company_email IS NOT NULL 
        ORDER BY supplier_name
    """)
    suppliers = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return request.app.state.templates.TemplateResponse("email/compose.html", {
        "request": request,
        "suppliers": suppliers
    })

@router.post("/send")
async def send_emails(
    supplier_ids: List[int] = Form(...),
    campaign_name: str = Form("Direct Outreach")
):
    """Send emails to selected suppliers"""
    result = email_crm.send_bulk_emails(supplier_ids, campaign_name)
    return JSONResponse(result)

@router.get("/t/{tracking_id}.gif")
async def track_open(tracking_id: str):
    """Email open tracking pixel"""
    tracker = EmailTracker(os.getenv('DATABASE_URL'))
    tracker.track_open(tracking_id)
    
    # Return 1x1 transparent GIF
    return Response(
        content=tracker.get_pixel_image(),
        media_type="image/gif",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"}
    )

@router.get("/c/{tracking_id}")
async def track_click(tracking_id: str, u: str = ""):
    """Track link click and redirect"""
    tracker = EmailTracker(os.getenv('DATABASE_URL'))
    tracker.track_click(tracking_id, u)
    
    # Redirect to URL or homepage
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=u or "https://fdx.trading")

@router.post("/ai/generate")
async def generate_ai_email(request: Request):
    """Generate email with AI"""
    data = await request.json()
    
    content = email_crm.generate_email(
        supplier={
            'name': data.get('name', 'Supplier'),
            'country': data.get('country', 'your country'),
            'products': data.get('products', '')
        },
        template_type=data.get('type', 'inquiry')
    )
    
    return JSONResponse({"content": content})

@router.get("/pipeline", response_class=HTMLResponse)
async def supplier_pipeline(request: Request):
    """Visual supplier pipeline"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get suppliers by stage
    cur.execute("""
        WITH supplier_status AS (
            SELECT 
                s.id, s.supplier_name, s.country, s.company_email,
                CASE 
                    WHEN r.interested = true THEN 'interested'
                    WHEN e.opened_at IS NOT NULL THEN 'opened'
                    WHEN e.id IS NOT NULL THEN 'contacted'
                    ELSE 'new'
                END as stage,
                e.sent_at, e.opened_at, r.received_at
            FROM suppliers s
            LEFT JOIN email_log e ON s.id = e.supplier_id
            LEFT JOIN email_responses r ON r.from_email = s.company_email
            WHERE s.company_email IS NOT NULL
        )
        SELECT * FROM supplier_status
        ORDER BY 
            CASE stage 
                WHEN 'interested' THEN 1
                WHEN 'opened' THEN 2
                WHEN 'contacted' THEN 3
                ELSE 4
            END,
            supplier_name
    """)
    
    suppliers = cur.fetchall()
    
    # Group by stage
    pipeline = {
        'new': [],
        'contacted': [],
        'opened': [],
        'interested': []
    }
    
    for supplier in suppliers:
        pipeline[supplier['stage']].append(supplier)
    
    cur.close()
    conn.close()
    
    return request.app.state.templates.TemplateResponse("email/pipeline.html", {
        "request": request,
        "pipeline": pipeline
    })

@router.post("/analyze-response")
async def analyze_response(request: Request):
    """Analyze email response with AI"""
    data = await request.json()
    
    result = email_crm.analyze_response(
        email_text=data.get('text', ''),
        from_email=data.get('from', '')
    )
    
    return JSONResponse(result)