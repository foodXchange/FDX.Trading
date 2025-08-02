"""
Demo Scheduling Routes
Handles demo request and scheduling functionality
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
import os
from datetime import datetime
from typing import Optional
from foodxchange.services.email_service import get_azure_email_service

logger = logging.getLogger(__name__)

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

# Create router
router = APIRouter(tags=["demo"])

# Import branding configuration
try:
    from foodxchange.config.branding import get_branding_context
except ImportError:
    # Fallback if branding module not available
    def get_branding_context(request):
        return {"request": request}

@router.get('/demo', response_class=HTMLResponse)
async def demo_page(request: Request):
    """Display demo scheduling page"""
    return templates.TemplateResponse('pages/schedule_demo.html', get_branding_context(request))

@router.post('/demo/schedule')
async def schedule_demo(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    company: str = Form(...),
    job_title: str = Form(...),
    company_size: str = Form(...),
    industry: str = Form(...),
    interests: str = Form(...),
    timezone: str = Form(...),
    preferred_date: str = Form(...),
    preferred_time: str = Form(...),
    message: Optional[str] = Form(None),
    consent: str = Form(...)
):
    """Handle demo scheduling form submission"""
    try:
        # Parse interests
        interest_list = interests.split(',') if interests else []
        
        # Format demo details
        demo_details = {
            'name': f"{first_name} {last_name}",
            'email': email,
            'phone': phone,
            'company': company,
            'job_title': job_title,
            'company_size': company_size,
            'industry': industry,
            'interests': interest_list,
            'timezone': timezone,
            'preferred_date': preferred_date,
            'preferred_time': preferred_time,
            'message': message or 'No additional information provided',
            'submitted_at': datetime.now().isoformat()
        }
        
        # Send notification email to sales team
        email_service = get_azure_email_service()
        
        # Create email content
        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8f9fa; }}
                .details-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .details-table th {{ background: #e9ecef; padding: 10px; text-align: left; width: 30%; }}
                .details-table td {{ padding: 10px; background: white; border: 1px solid #dee2e6; }}
                .interests {{ background: white; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .message-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>New Demo Request</h1>
            </div>
            <div class="content">
                <h2>Contact Information</h2>
                <table class="details-table">
                    <tr>
                        <th>Name</th>
                        <td>{demo_details['name']}</td>
                    </tr>
                    <tr>
                        <th>Email</th>
                        <td><a href="mailto:{demo_details['email']}">{demo_details['email']}</a></td>
                    </tr>
                    <tr>
                        <th>Phone</th>
                        <td>{demo_details['phone']}</td>
                    </tr>
                    <tr>
                        <th>Company</th>
                        <td>{demo_details['company']}</td>
                    </tr>
                    <tr>
                        <th>Job Title</th>
                        <td>{demo_details['job_title']}</td>
                    </tr>
                    <tr>
                        <th>Company Size</th>
                        <td>{demo_details['company_size']}</td>
                    </tr>
                    <tr>
                        <th>Industry</th>
                        <td>{demo_details['industry']}</td>
                    </tr>
                </table>
                
                <h2>Demo Preferences</h2>
                <table class="details-table">
                    <tr>
                        <th>Preferred Date</th>
                        <td>{demo_details['preferred_date']}</td>
                    </tr>
                    <tr>
                        <th>Preferred Time</th>
                        <td>{demo_details['preferred_time']} ({demo_details['timezone']})</td>
                    </tr>
                </table>
                
                <div class="interests">
                    <h3>Areas of Interest</h3>
                    <ul>
                        {"".join([f"<li>{interest.replace('_', ' ').title()}</li>" for interest in demo_details['interests']])}
                    </ul>
                </div>
                
                <div class="message-box">
                    <h3>Additional Information</h3>
                    <p>{demo_details['message']}</p>
                </div>
                
                <p><small>Submitted on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</small></p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        email_text = f"""
New Demo Request

Contact Information:
Name: {demo_details['name']}
Email: {demo_details['email']}
Phone: {demo_details['phone']}
Company: {demo_details['company']}
Job Title: {demo_details['job_title']}
Company Size: {demo_details['company_size']}
Industry: {demo_details['industry']}

Demo Preferences:
Preferred Date: {demo_details['preferred_date']}
Preferred Time: {demo_details['preferred_time']} ({demo_details['timezone']})

Areas of Interest:
{chr(10).join(['- ' + interest.replace('_', ' ').title() for interest in demo_details['interests']])}

Additional Information:
{demo_details['message']}

---
Submitted on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        # Send to sales team
        await email_service.send_product_brief(
            recipient_emails=[os.getenv('SALES_EMAIL', 'sales@foodxchange.com')],
            subject=f"New Demo Request - {company} ({first_name} {last_name})",
            body_html=email_html,
            body_text=email_text
        )
        
        # Send confirmation to user
        confirmation_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #667eea; color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 40px; max-width: 600px; margin: 0 auto; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Demo Request Received!</h1>
            </div>
            <div class="content">
                <p>Hi {first_name},</p>
                
                <p>Thank you for your interest in FoodXchange! We've received your demo request and our team will reach out within 24 hours to confirm your preferred time slot.</p>
                
                <h3>Your Demo Details:</h3>
                <ul>
                    <li><strong>Date:</strong> {demo_details['preferred_date']}</li>
                    <li><strong>Time:</strong> {demo_details['preferred_time']} ({demo_details['timezone']})</li>
                    <li><strong>Duration:</strong> 30 minutes</li>
                </ul>
                
                <h3>What to Expect:</h3>
                <ul>
                    <li>Personalized platform walkthrough</li>
                    <li>Live demonstration of key features</li>
                    <li>ROI calculation for your business</li>
                    <li>Q&A session with our experts</li>
                </ul>
                
                <p>In the meantime, feel free to explore our resources:</p>
                <p><a href="https://foodxchange.com/resources" class="button">View Resources</a></p>
                
                <p>If you have any questions before the demo, don't hesitate to reach out!</p>
                
                <p>Best regards,<br>
                The FoodXchange Team</p>
            </div>
            <div class="footer">
                <p>FoodXchange - AI-Powered B2B Food Sourcing Platform</p>
            </div>
        </body>
        </html>
        """
        
        confirmation_text = f"""
Hi {first_name},

Thank you for your interest in FoodXchange! We've received your demo request and our team will reach out within 24 hours to confirm your preferred time slot.

Your Demo Details:
- Date: {demo_details['preferred_date']}
- Time: {demo_details['preferred_time']} ({demo_details['timezone']})
- Duration: 30 minutes

What to Expect:
- Personalized platform walkthrough
- Live demonstration of key features
- ROI calculation for your business
- Q&A session with our experts

If you have any questions before the demo, don't hesitate to reach out!

Best regards,
The FoodXchange Team
        """
        
        # Send confirmation email
        await email_service.send_product_brief(
            recipient_emails=[email],
            subject="Your FoodXchange Demo Request - Confirmation",
            body_html=confirmation_html,
            body_text=confirmation_text
        )
        
        logger.info(f"Demo request submitted: {company} - {email}")
        
        return JSONResponse(
            content={'success': True, 'message': 'Demo scheduled successfully'},
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error scheduling demo: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule demo")

# Demo data for animation showcase
DEMO_STATS = {
    "suppliers": 10000,
    "countries": 150, 
    "transactions": 500,
    "success_rate": 95,
    "active_rfqs": 234,
    "response_time": "2.3"
}

DEMO_FEATURES = [
    {
        "title": "Smart AI Matching",
        "description": "Our AI analyzes your requirements and instantly connects you with the most suitable suppliers",
        "icon": "fa-brain",
        "delay": "0"
    },
    {
        "title": "Verified Network", 
        "description": "Every supplier and buyer is pre-verified with compliance checks and certifications",
        "icon": "fa-shield-alt",
        "delay": "0.1"
    },
    {
        "title": "Global Reach",
        "description": "Access suppliers from 150+ countries with real-time translation and currency conversion",
        "icon": "fa-globe",
        "delay": "0.2"
    },
    {
        "title": "Real-time Analytics",
        "description": "Track market trends, price fluctuations, and optimize your supply chain decisions",
        "icon": "fa-chart-line", 
        "delay": "0.3"
    }
]

DEMO_WORKFLOW = [
    {
        "step": 1,
        "title": "Post Your Requirements",
        "description": "Create detailed RFQs with our smart forms that capture every specification",
        "icon": "fa-file-alt",
        "color": "primary"
    },
    {
        "step": 2,
        "title": "AI Matching Engine",
        "description": "Our algorithm analyzes your needs and matches you with verified suppliers",
        "icon": "fa-robot",
        "color": "info"
    },
    {
        "step": 3,
        "title": "Compare & Negotiate",
        "description": "Review offers side-by-side and communicate directly with suppliers",
        "icon": "fa-comments",
        "color": "warning"
    },
    {
        "step": 4,
        "title": "Secure Transaction",
        "description": "Complete deals with integrated payments and automated documentation",
        "icon": "fa-handshake",
        "color": "success"
    }
]

@router.get('/demo/animations', response_class=HTMLResponse)
async def demo_animations(request: Request):
    """Display animated demo page showcasing GSAP animations"""
    context = get_branding_context(request)
    context.update({
        "stats": DEMO_STATS,
        "features": DEMO_FEATURES,
        "workflow": DEMO_WORKFLOW,
        "page_title": "FoodXchange Demo - See It In Action"
    })
    return templates.TemplateResponse('pages/demo_animated.html', context)

@router.get('/demo/test', response_class=HTMLResponse)
async def gsap_test(request: Request):
    """Simple GSAP test page"""
    return templates.TemplateResponse('pages/gsap_test.html', get_branding_context(request))