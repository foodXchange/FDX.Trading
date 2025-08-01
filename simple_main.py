"""
FoodXchange (FDX) - AI-Powered B2B Food Sourcing Platform
Simplified main application for modern homepage
"""

import os
from pathlib import Path
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Configuration class following FDX standards
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fdx-homepage-secret-key-2024'
    FDX_ADMIN = os.environ.get('FDX_ADMIN') or 'admin@fdx.trading'
    CORS_ORIGINS = [
        "https://fdx.trading",
        "https://www.fdx.trading", 
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8003",
        "http://localhost:9000"
    ]
    API_RATE_LIMIT = '100 per hour'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
# Initialize config
config = Config()

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Create FastAPI app following FDX standards
app = FastAPI(
    title="FoodXchange (FDX)",
    description="AI-Powered B2B Food Sourcing Platform - Homepage Service",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Add CORS middleware with FDX configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-Total-Count", "X-Request-ID"],
    max_age=86400,
)

# Mount static files following FDX directory structure
static_dir = BASE_DIR / "foodxchange" / "static"
template_dir = BASE_DIR / "foodxchange" / "templates"

# Verify directories exist
if not static_dir.exists():
    logger.warning(f"Static directory not found: {static_dir}")
    static_dir = BASE_DIR / "static"  # Fallback

if not template_dir.exists():
    logger.warning(f"Template directory not found: {template_dir}")
    template_dir = BASE_DIR / "templates"  # Fallback

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(template_dir))

# Add custom template functions
def url_for(name: str, **path_params) -> str:
    """Simple URL builder for templates"""
    routes = {
        "static": "/static",
        "landing": "/",
        "dashboard": "/dashboard",
        "login_page": "/login",
    }
    
    if name == "static" and "filename" in path_params:
        return f"/static/{path_params['filename']}"
    
    return routes.get(name, "/")

# Add url_for to template globals
templates.env.globals["url_for"] = url_for

# Pydantic models for API requests
class ContactRequest(BaseModel):
    name: str
    email: str
    message: str
    company: Optional[str] = None

class DemoRequest(BaseModel):
    name: str
    email: str
    company: str
    phone: Optional[str] = None
    preferred_time: Optional[str] = None

class TrialRequest(BaseModel):
    name: str
    email: str
    company: str
    company_size: str
    country: str

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and context"""
    import time
    import uuid
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Start timing
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": request.client.host if request.client else "unknown"
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Calculate duration
        duration = time.time() - start_time
        
        # Log error
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "duration_ms": round(duration * 1000, 2),
                "error": str(e),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": request.client.host if request.client else "unknown"
            }
        )
        raise

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page using Jinja2 template"""
    try:
        context = {
            'request': request,
            'company_name': 'FoodXchange (FDX)',
            'tagline': 'AI-Powered B2B Food Trading Platform',
            'current_year': datetime.now().year,
            'stats': {
                'time_saved': 50,
                'cost_reduction': 30,
                'compliance_rate': 95,
                'faster_negotiations': 50,
                'on_time_delivery': 95,
                'revenue_growth': 30
            },
            'benefits': {
                'buyers': [
                    '50% Time Savings: Automate procurement workflows from RFQ to delivery',
                    'Global Supplier Network: Access pre-verified suppliers across 50+ countries',
                    'AI Price Intelligence: Get market insights and optimize procurement costs',
                    'Risk Mitigation: Real-time compliance tracking and quality assurance',
                    'Centralized Control: Manage multiple locations and teams from one dashboard',
                    'Data-Driven Decisions: Analytics and reporting for strategic sourcing'
                ],
                'sellers': [
                    '3x More Opportunities: AI matches you with relevant RFQs automatically',
                    'Faster Deal Closure: Streamlined negotiation and order processing',
                    'Global Market Access: Reach international buyers without barriers',
                    'Automated Compliance: Upload certifications once, use everywhere',
                    'Competitive Intelligence: Market insights to optimize your offerings',
                    'Payment Security: Guaranteed transactions with escrow protection'
                ]
            },
            'workflow_steps': [
                {
                    'number': 1,
                    'icon': 'fa-file-invoice',
                    'title': 'Create Smart RFQ',
                    'description': 'AI assists in creating detailed RFQs with product specs, quantities, and delivery requirements'
                },
                {
                    'number': 2,
                    'icon': 'fa-broadcast-tower',
                    'title': 'Intelligent Distribution',
                    'description': 'Machine learning matches your RFQ with verified suppliers based on capability and compliance'
                },
                {
                    'number': 3,
                    'icon': 'fa-chart-line',
                    'title': 'Real-time Offers',
                    'description': 'Receive and compare offers side-by-side with transparent pricing and terms'
                },
                {
                    'number': 4,
                    'icon': 'fa-handshake',
                    'title': 'Smart Negotiation',
                    'description': 'AI-powered insights help negotiate better terms while maintaining relationships'
                },
                {
                    'number': 5,
                    'icon': 'fa-truck',
                    'title': 'Track & Deliver',
                    'description': 'Real-time tracking from order confirmation to delivery with automated documentation'
                }
            ],
            'ai_features': [
                {
                    'icon': 'fa-brain',
                    'title': 'Intelligent Matching',
                    'description': 'AI analyzes buyer requirements and supplier capabilities for perfect matches'
                },
                {
                    'icon': 'fa-chart-bar',
                    'title': 'Price Prediction',
                    'description': 'Machine learning models predict market trends and optimal pricing strategies'
                },
                {
                    'icon': 'fa-shield-alt',
                    'title': 'Risk Assessment',
                    'description': 'Automated evaluation of supplier reliability and compliance history'
                },
                {
                    'icon': 'fa-robot',
                    'title': 'Smart Automation',
                    'description': 'Intelligent workflow automation that learns and improves with each transaction'
                }
            ],
            'about_stats': {
                'transaction_volume': '$50M+',
                'enterprise_clients': '500+',
                'countries_served': '50+',
                'active_suppliers': '10K+'
            }
        }
        return templates.TemplateResponse("pages/index.html", context)
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.post("/api/contact")
async def contact(contact_data: ContactRequest):
    """Handle contact form submissions"""
    try:
        logger.info(f"Contact request received from {contact_data.email}")
        return JSONResponse(
            content={
                'status': 'success',
                'message': 'Thank you for contacting us. We will get back to you soon.'
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return JSONResponse(
            content={
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            },
            status_code=500
        )

@app.post("/api/demo")
async def request_demo(demo_data: DemoRequest):
    """Handle demo request submissions"""
    try:
        logger.info(f"Demo request received from {demo_data.email} for {demo_data.company}")
        return JSONResponse(
            content={
                'status': 'success',
                'message': 'Demo request received. Our team will contact you within 24 hours.'
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Demo request error: {e}")
        return JSONResponse(
            content={
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            },
            status_code=500
        )

@app.post("/api/trial")
async def start_trial(trial_data: TrialRequest):
    """Handle trial signup submissions"""
    try:
        logger.info(f"Trial request received from {trial_data.email} for {trial_data.company}")
        return JSONResponse(
            content={
                'status': 'success',
                'message': 'Your free trial has been activated. Check your email for login details.'
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Trial request error: {e}")
        return JSONResponse(
            content={
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            },
            status_code=500
        )

# Error handlers
@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def server_error(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FDX Homepage Service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FoodXchange application...")
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )