"""
Footer Pages Routes
Handles all static pages linked from the footer
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
from foodxchange.services.email_service import get_azure_email_service

logger = logging.getLogger(__name__)

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

# Create router
router = APIRouter(tags=["footer"])

# Import branding configuration
try:
    from foodxchange.config.branding import (
        COMPANY, CONTACT, SOCIAL_MEDIA, STATS, 
        TRUST_BADGES, KEY_FEATURES, CTA_MESSAGES
    )
except ImportError:
    # Fallback configuration if branding.py is not available
    COMPANY = {
        "name": "FDX Trading",
        "legal_name": "FDX Trading Ltd.",
        "domain": "fdx.trading",
        "tagline": "AI-Powered Global Food Sourcing Platform"
    }
    CONTACT = {
        "email": "info@fdx.trading",
        "phone": "+972-52-5222291",
        "address": "Tel Aviv, Israel"
    }
    SOCIAL_MEDIA = {
        "linkedin": "https://linkedin.com/company/fdx-trading",
        "facebook": "https://facebook.com/fdxtrading",
        "twitter": "https://x.com/fdx_trading",
        "instagram": "https://instagram.com/fdx.trading",
        "youtube": "https://youtube.com/@fdxtrading"
    }
    # Fallback values for missing branding variables
    STATS = {
        "users": "10,000+",
        "countries": "50+",
        "deals": "100,000+",
        "savings": "$2M+"
    }
    TRUST_BADGES = [
        {"name": "ISO 27001", "icon": "fas fa-shield-alt"},
        {"name": "GDPR Compliant", "icon": "fas fa-lock"},
        {"name": "SOC 2 Type II", "icon": "fas fa-certificate"}
    ]
    CTA_MESSAGES = {
        "primary": "Start Trading Today",
        "secondary": "Get Your Free Demo"
    }

# Create context with branding data
def get_branding_context(request: Request):
    """Get context with all branding data"""
    return {
        "request": request,
        "company": COMPANY,
        "contact": CONTACT,
        "social_media": SOCIAL_MEDIA,
        "stats": STATS,
        "trust_badges": TRUST_BADGES,
        "cta_messages": CTA_MESSAGES
    }

# Platform Pages
@router.get('/features', response_class=HTMLResponse)
async def features(request: Request):
    """Platform features page"""
    return templates.TemplateResponse('pages/features.html', get_branding_context(request))

@router.get('/pricing', response_class=HTMLResponse)
async def pricing(request: Request):
    """Pricing plans page"""
    return templates.TemplateResponse('pages/pricing.html', get_branding_context(request))

@router.get('/security', response_class=HTMLResponse)
async def security(request: Request):
    """Security information page"""
    return templates.TemplateResponse('pages/security.html', get_branding_context(request))

@router.get('/api', response_class=HTMLResponse)
async def api(request: Request):
    """API documentation page"""
    return templates.TemplateResponse('pages/api.html', get_branding_context(request))

# Solutions Pages
@router.get('/for-buyers', response_class=HTMLResponse)
async def for_buyers(request: Request):
    """Solutions for buyers page"""
    return templates.TemplateResponse('pages/for_buyers.html', get_branding_context(request))

@router.get('/for-suppliers', response_class=HTMLResponse)
async def for_suppliers(request: Request):
    """Solutions for suppliers page"""
    return templates.TemplateResponse('pages/for_suppliers.html', get_branding_context(request))

@router.get('/for-brokers', response_class=HTMLResponse)
async def for_brokers(request: Request):
    """Solutions for brokers page"""
    return templates.TemplateResponse('pages/for_brokers.html', get_branding_context(request))

@router.get('/enterprise', response_class=HTMLResponse)
async def enterprise(request: Request):
    """Enterprise solutions page"""
    return templates.TemplateResponse('pages/enterprise.html', get_branding_context(request))

# Company Pages
@router.get('/about', response_class=HTMLResponse)
async def about(request: Request):
    """About us page"""
    return templates.TemplateResponse('pages/about.html', get_branding_context(request))

@router.get('/careers', response_class=HTMLResponse)
async def careers(request: Request):
    """Careers page"""
    return templates.TemplateResponse('pages/careers.html', get_branding_context(request))

@router.get('/blog', response_class=HTMLResponse)
async def blog(request: Request):
    """Blog page"""
    return templates.TemplateResponse('pages/blog.html', get_branding_context(request))

@router.get('/contact', response_class=HTMLResponse)
async def contact(request: Request):
    """Contact page"""
    return templates.TemplateResponse('pages/contact.html', get_branding_context(request))

@router.post('/contact')
async def contact_submit(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    phone: str = Form(None),
    company: str = Form(None),
    user_type: str = Form(None)
):
    """Handle contact form submission"""
    try:
        # Get form data
        form_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone or '',
            'company': company or '',
            'user_type': user_type or '',
            'subject': subject,
            'message': message
        }
        
        # Send email
        email_service = get_azure_email_service()
        result = await email_service.send_contact_form(contact_data)
        
        if result['success']:
            logger.info(f"Contact form email sent successfully from {email}: {subject}")
            # Redirect back to contact page with success message
            return RedirectResponse(url="/contact?success=true", status_code=303)
        else:
            logger.error(f"Failed to send contact form email: {result.get('error', 'Unknown error')}")
            # Still show success to user but log the error
            return RedirectResponse(url="/contact?success=true", status_code=303)
        
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        return RedirectResponse(url="/contact?error=true", status_code=303)

# Additional utility routes
@router.get('/privacy', response_class=HTMLResponse)
async def privacy(request: Request):
    """Privacy policy page"""
    return templates.TemplateResponse('pages/privacy.html', get_branding_context(request))

@router.get('/terms', response_class=HTMLResponse)
async def terms(request: Request):
    """Terms of service page"""
    return templates.TemplateResponse('pages/terms.html', get_branding_context(request))

# Redirect old URLs to new ones (for backwards compatibility)
@router.get('/for_buyers')
async def for_buyers_redirect():
    return RedirectResponse(url="/for-buyers", status_code=301)

@router.get('/for_suppliers')
async def for_suppliers_redirect():
    return RedirectResponse(url="/for-suppliers", status_code=301)

@router.get('/for_brokers')
async def for_brokers_redirect():
    return RedirectResponse(url="/for-brokers", status_code=301)