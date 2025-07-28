import warnings
import time
import os
import logging
import platform
from datetime import datetime, timedelta

# Load all environment variables from .env and .env.blob files
from foodxchange.load_all_env import load_all_env_files

# Suppress cryptography warnings about 32-bit Python
warnings.filterwarnings("ignore", message=".*cryptography.*32-bit.*64-bit.*")

# Enhanced Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

# Initialize Sentry SDK with the new DSN
sentry_sdk.init(
    dsn="https://fdf092923fb6dd5351274f42e8a4dee9@o4509734929104896.ingest.de.sentry.io/4509734959775824",
    # Add data like request headers and IP for users
    send_default_pii=True,
    # Set sample rate for performance monitoring
    traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
    # Set the environment
    environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
    # Add integrations
    integrations=[
        FastApiIntegration(
            transaction_style="endpoint"  # Use endpoint name as transaction name
        ),
        SqlalchemyIntegration(),
        HttpxIntegration(),
    ],
    # Set release tracking
    release=os.getenv("SENTRY_RELEASE", "foodxchange@1.0.0"),
    # Enable profiling
    profiles_sample_rate=1.0,  # Profile 100% of sampled transactions
    # Attach stack trace to messages
    attach_stacktrace=True,
    # Sample rate for error events
    sample_rate=1.0,
    # Max breadcrumbs
    max_breadcrumbs=50,
)

print("Sentry SDK initialized with new DSN")

# Try to import middleware if available
try:
    from sentry_middleware import SentryMiddleware, SentryUserMiddleware, db_monitor
    print("Sentry middleware imported successfully")
except ImportError:
    print("Warning: Sentry middleware not found")

from fastapi import FastAPI, Request, Form, HTTPException, Depends, Body, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
import psutil

from foodxchange.database import get_db
from foodxchange.auth import SessionAuth, get_current_user_context as get_user_context

# Import and include authentication routes
from foodxchange.routes.auth_routes import include_auth_routes

# Azure Monitor integration
try:
    from foodxchange.services.azure_monitor_service import azure_monitor
    print("Azure Monitor service imported")
except ImportError as e:
    print(f"Warning: Azure Monitor service not available: {e}")
    azure_monitor = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FoodXchange API")

# Add enhanced Sentry middleware
try:
    app.add_middleware(SentryMiddleware)
    app.add_middleware(SentryUserMiddleware)
except:
    pass

# Add Azure Monitor middleware if available
if azure_monitor and azure_monitor.enabled:
    try:
        azure_middleware = azure_monitor.get_fastapi_middleware()
        if azure_middleware:
            app.add_middleware(azure_middleware)
            print("Azure Monitor middleware added")
    except Exception as e:
        print(f"Warning: Failed to add Azure Monitor middleware: {e}")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="foodxchange/static"), name="static")

# Templates
templates = Jinja2Templates(directory="foodxchange/templates")

# Include authentication routes
include_auth_routes(app)

# Global start time for uptime tracking
start_time = time.time()

def get_current_user_context(request: Request, db: Session):
    return get_user_context(request, db)

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Simple test page to check if templates are working"""
    return HTMLResponse(content="""
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Page Working!</h1>
            <p>If you can see this, the server is working correctly.</p>
            <a href="/dashboard">Try Dashboard</a>
            <a href="/dashboard-simple">Try Simple Dashboard</a>
            <a href="/test-template">Try Template Test</a>
        </body>
    </html>
    """)

@app.get("/test-template", response_class=HTMLResponse)
async def test_template(request: Request):
    """Test template page - Bootstrap styled"""
    try:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Template - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Test Template</h1>
                                <p class="text-muted mb-0 font-roboto-serif">Testing Bootstrap template rendering</p>
                            </div>
                            <div class="btn-group">
                                <a href="/dashboard" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Dashboard
                                </a>
                            </div>
                        </div>

                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-check-circle me-2"></i>Template Test Successful
                                        </h5>
                                    </div>
                                    <div class="card-body text-center">
                                        <div class="mb-4">
                                            <i class="bi bi-check-circle text-success" style="font-size: 4rem;"></i>
                                        </div>
                                        <h4 class="font-causten mb-3">Bootstrap Template Working!</h4>
                                        <p class="font-roboto-serif text-muted mb-4">
                                            This page confirms that Bootstrap templates are rendering correctly without Jinja2.
                                        </p>
                                        <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                                            <a href="/dashboard" class="btn btn-primary font-causten">
                                                <i class="bi bi-speedometer2 me-2"></i>Go to Dashboard
                                            </a>
                                            <a href="/test" class="btn btn-outline-primary font-causten">
                                                <i class="bi bi-gear me-2"></i>Test Page
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Test template error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Test Template Error</title></head>
            <body>
                <h1>Test Template Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard">Back to Dashboard</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/test-simple-template", response_class=HTMLResponse)
async def test_simple_template(request: Request):
    """Simple test template page - Bootstrap styled"""
    try:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Simple Test - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card border-0 shadow-sm">
                            <div class="card-body text-center">
                                <h2 class="font-causten mb-3">Simple Test Page</h2>
                                <p class="font-roboto-serif text-muted">This is a simple Bootstrap template test.</p>
                                <a href="/dashboard" class="btn btn-primary font-causten">Back to Dashboard</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Simple test template error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Simple Test Error</title></head>
            <body>
                <h1>Simple Test Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard">Back to Dashboard</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/dashboard-simple", response_class=HTMLResponse)
async def dashboard_simple(request: Request):
    """Simple dashboard page - Bootstrap styled"""
    try:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Simple Dashboard - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Simple Dashboard</h1>
                                <p class="text-muted mb-0 font-roboto-serif">Streamlined dashboard view</p>
                            </div>
                            <div class="btn-group">
                                <a href="/dashboard" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Full Dashboard
                                </a>
                            </div>
                        </div>

                        <div class="row g-4">
                            <div class="col-xl-3 col-md-6">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-body text-center">
                                        <div class="d-flex align-items-center justify-content-center mb-2">
                                            <i class="bi bi-building text-primary fs-1"></i>
                                        </div>
                                        <h3 class="text-primary mb-1 font-causten">12</h3>
                                        <p class="text-muted mb-0 font-roboto-serif">Suppliers</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-body text-center">
                                        <div class="d-flex align-items-center justify-content-center mb-2">
                                            <i class="bi bi-file-earmark-text text-success fs-1"></i>
                                        </div>
                                        <h3 class="text-success mb-1 font-causten">24</h3>
                                        <p class="text-muted mb-0 font-roboto-serif">RFQs</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-body text-center">
                                        <div class="d-flex align-items-center justify-content-center mb-2">
                                            <i class="bi bi-cart text-info fs-1"></i>
                                        </div>
                                        <h3 class="text-info mb-1 font-causten">8</h3>
                                        <p class="text-muted mb-0 font-roboto-serif">Orders</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-body text-center">
                                        <div class="d-flex align-items-center justify-content-center mb-2">
                                            <i class="bi bi-currency-dollar text-warning fs-1"></i>
                                        </div>
                                        <h3 class="text-warning mb-1 font-causten">$45K</h3>
                                        <p class="text-muted mb-0 font-roboto-serif">Total Spend</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Dashboard simple error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Dashboard Simple Error</title></head>
            <body>
                <h1>Dashboard Simple Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard">Back to Dashboard</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request, db: Session = Depends(get_db)):
    """Landing page - Bootstrap styled"""
    try:
        # Get current user context
        current_user = None
        try:
            current_user = get_current_user_context(request, db)
        except Exception as e:
            print(f"User context error: {e}")
            current_user = None

        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>foodXchange - Food Supply Chain Management</title>
            
            <!-- Comprehensive Favicon Setup -->
            <link rel="icon" type="image/png" sizes="32x32" href="/static/brand/logos/Favicon.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/static/brand/logos/Favicon.png">
            <link rel="shortcut icon" href="/static/brand/logos/Favicon.png">
            <link rel="apple-touch-icon" href="/static/brand/logos/Favicon.png">
            <link rel="icon" href="/favicon.ico">
            
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
            <style>
                .hero-section {{
                    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
                    color: white;
                    padding: 4rem 0;
                }}
                .hero-logo {{
                    max-height: 80px;
                    filter: brightness(0) invert(1);
                }}
                .feature-card {{
                    transition: transform 0.3s ease;
                }}
                .feature-card:hover {{
                    transform: translateY(-5px);
                }}
                .stats-section {{
                    background-color: #f8f9fa;
                    padding: 3rem 0;
                }}
                .cta-section {{
                    background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
                    color: white;
                    padding: 3rem 0;
                }}
            </style>
        </head>
        <body>
            <!-- Navigation -->
            <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
                <div class="container">
                    <a class="navbar-brand d-flex align-items-center" href="/">
                        <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                             alt="foodXchange" height="40" class="me-2">
                        <span class="font-causten fw-bold fs-4">foodXchange</span>
                    </a>
                    
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item">
                                <a class="nav-link font-causten" href="#features">Features</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link font-causten" href="#about">About</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link font-causten" href="#contact">Contact</a>
                            </li>
                            {'<li class="nav-item dropdown">' if current_user else ''}
                            {'<a class="nav-link dropdown-toggle font-causten" href="#" role="button" data-bs-toggle="dropdown">' if current_user else ''}
                            {'<i class="bi bi-person-circle me-1"></i>' if current_user else ''}
                            {'Guest User' if current_user else ''}
                            {'</a>' if current_user else ''}
                            {'<ul class="dropdown-menu">' if current_user else ''}
                            {'<li><a class="dropdown-item font-causten" href="/dashboard">Dashboard</a></li>' if current_user else ''}
                            {'<li><a class="dropdown-item font-causten" href="/profile">Profile</a></li>' if current_user else ''}
                            {'<li><hr class="dropdown-divider"></li>' if current_user else ''}
                            {'<li><a class="dropdown-item font-causten" href="/logout">Logout</a></li>' if current_user else ''}
                            {'</ul>' if current_user else ''}
                            {'</li>' if current_user else ''}
                            {'<li class="nav-item">' if not current_user else ''}
                            {'<a class="nav-link font-causten" href="/login">Login</a>' if not current_user else ''}
                            {'</li>' if not current_user else ''}
                            {'<li class="nav-item">' if not current_user else ''}
                            {'<a class="btn btn-primary font-causten ms-2" href="/register">Get Started</a>' if not current_user else ''}
                            {'</li>' if not current_user else ''}
                        </ul>
                    </div>
                </div>
            </nav>

            <!-- Hero Section -->
            <section class="hero-section">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-lg-6">
                            <div class="d-flex align-items-center mb-4">
                                <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                                     alt="foodXchange" class="hero-logo me-3">
                                <div>
                                    <h1 class="display-4 font-causten fw-bold mb-3">foodXchange</h1>
                                    <p class="lead font-roboto-serif mb-0">Revolutionizing Food Supply Chain Management</p>
                                </div>
                            </div>
                            <h2 class="h3 font-causten mb-4">Streamline Your Food Procurement Process</h2>
                            <p class="font-roboto-serif mb-4">
                                Connect with suppliers, manage RFQs, track orders, and optimize your food supply chain 
                                with our comprehensive platform designed for the modern food industry.
                            </p>
                            <div class="d-flex gap-3">
                                <a href="/register" class="btn btn-light btn-lg font-causten">
                                    <i class="bi bi-rocket-takeoff me-2"></i>Get Started Free
                                </a>
                                <a href="#features" class="btn btn-outline-light btn-lg font-causten">
                                    <i class="bi bi-play-circle me-2"></i>Learn More
                                </a>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="text-center">
                                <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                                     alt="Platform Preview" class="img-fluid" style="max-height: 400px;">
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Features Section -->
            <section id="features" class="py-5">
                <div class="container">
                    <div class="row text-center mb-5">
                        <div class="col-lg-8 mx-auto">
                            <h2 class="display-5 font-causten mb-3">Why Choose foodXchange?</h2>
                            <p class="lead font-roboto-serif text-muted">
                                Comprehensive tools designed specifically for food industry professionals
                            </p>
                        </div>
                    </div>
                    
                    <div class="row g-4">
                        <div class="col-lg-4 col-md-6">
                            <div class="card border-0 shadow-sm feature-card h-100">
                                <div class="card-body text-center p-4">
                                    <div class="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                        <i class="bi bi-building text-primary fs-1"></i>
                                    </div>
                                    <h4 class="font-causten mb-3">Supplier Management</h4>
                                    <p class="font-roboto-serif text-muted">
                                        Manage your supplier network, track performance, and maintain detailed profiles 
                                        with contact information and capabilities.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-4 col-md-6">
                            <div class="card border-0 shadow-sm feature-card h-100">
                                <div class="card-body text-center p-4">
                                    <div class="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                        <i class="bi bi-file-earmark-text text-success fs-1"></i>
                                    </div>
                                    <h4 class="font-causten mb-3">RFQ Management</h4>
                                    <p class="font-roboto-serif text-muted">
                                        Create and manage Request for Quotations, send to multiple suppliers, 
                                        and track responses in real-time.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-4 col-md-6">
                            <div class="card border-0 shadow-sm feature-card h-100">
                                <div class="card-body text-center p-4">
                                    <div class="bg-info bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                        <i class="bi bi-cart text-info fs-1"></i>
                                    </div>
                                    <h4 class="font-causten mb-3">Order Tracking</h4>
                                    <p class="font-roboto-serif text-muted">
                                        Track orders from placement to delivery, monitor status updates, 
                                        and manage inventory efficiently.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-4 col-md-6">
                            <div class="card border-0 shadow-sm feature-card h-100">
                                <div class="card-body text-center p-4">
                                    <div class="bg-warning bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                        <i class="bi bi-graph-up text-warning fs-1"></i>
                                    </div>
                                    <h4 class="font-causten mb-3">Analytics & Insights</h4>
                                    <p class="font-roboto-serif text-muted">
                                        Get detailed analytics on spending patterns, supplier performance, 
                                        and market trends to make informed decisions.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-4 col-md-6">
                            <div class="card border-0 shadow-sm feature-card h-100">
                                <div class="card-body text-center p-4">
                                    <div class="bg-danger bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                        <i class="bi bi-robot text-danger fs-1"></i>
                                    </div>
                                    <h4 class="font-causten mb-3">AI-Powered Automation</h4>
                                    <p class="font-roboto-serif text-muted">
                                        Leverage artificial intelligence for automated supplier matching, 
                                        price optimization, and intelligent recommendations.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-4 col-md-6">
                            <div class="card border-0 shadow-sm feature-card h-100">
                                <div class="card-body text-center p-4">
                                    <div class="bg-secondary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                        <i class="bi bi-shield-check text-secondary fs-1"></i>
                                    </div>
                                    <h4 class="font-causten mb-3">Compliance & Safety</h4>
                                    <p class="font-roboto-serif text-muted">
                                        Ensure food safety compliance, track certifications, and maintain 
                                        audit trails for regulatory requirements.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Stats Section -->
            <section class="stats-section">
                <div class="container">
                    <div class="row text-center">
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="d-flex align-items-center justify-content-center mb-2">
                                <i class="bi bi-building text-primary fs-1"></i>
                            </div>
                            <h3 class="text-primary font-causten">500+</h3>
                            <p class="font-roboto-serif text-muted">Active Suppliers</p>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="d-flex align-items-center justify-content-center mb-2">
                                <i class="bi bi-file-earmark-text text-success fs-1"></i>
                            </div>
                            <h3 class="text-success font-causten">10K+</h3>
                            <p class="font-roboto-serif text-muted">RFQs Processed</p>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="d-flex align-items-center justify-content-center mb-2">
                                <i class="bi bi-cart text-info fs-1"></i>
                            </div>
                            <h3 class="text-info font-causten">$50M+</h3>
                            <p class="font-roboto-serif text-muted">Orders Managed</p>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="d-flex align-items-center justify-content-center mb-2">
                                <i class="bi bi-people text-warning fs-1"></i>
                            </div>
                            <h3 class="text-warning font-causten">200+</h3>
                            <p class="font-roboto-serif text-muted">Happy Clients</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- CTA Section -->
            <section class="cta-section">
                <div class="container text-center">
                    <h2 class="display-5 font-causten mb-4">Ready to Transform Your Food Supply Chain?</h2>
                    <p class="lead font-roboto-serif mb-4">
                        Join hundreds of food industry professionals who trust foodXchange for their procurement needs.
                    </p>
                    <div class="d-flex gap-3 justify-content-center">
                        <a href="/register" class="btn btn-primary btn-lg font-causten">
                            <i class="bi bi-rocket-takeoff me-2"></i>Start Free Trial
                        </a>
                        <a href="#contact" class="btn btn-outline-light btn-lg font-causten">
                            <i class="bi bi-chat-dots me-2"></i>Contact Sales
                        </a>
                    </div>
                </div>
            </section>

            <!-- Footer -->
            <footer class="bg-dark text-light py-4">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-4 mb-4">
                            <div class="d-flex align-items-center mb-3">
                                <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                                     alt="foodXchange" height="30" class="me-2">
                                <span class="font-causten fw-bold">foodXchange</span>
                            </div>
                            <p class="font-roboto-serif text-muted">
                                Revolutionizing food supply chain management with innovative technology and 
                                industry expertise.
                            </p>
                        </div>
                        <div class="col-lg-2 col-md-6 mb-4">
                            <h5 class="font-causten mb-3">Product</h5>
                            <ul class="list-unstyled">
                                <li><a href="#features" class="text-muted text-decoration-none font-roboto-serif">Features</a></li>
                                <li><a href="/pricing" class="text-muted text-decoration-none font-roboto-serif">Pricing</a></li>
                                <li><a href="/api" class="text-muted text-decoration-none font-roboto-serif">API</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-2 col-md-6 mb-4">
                            <h5 class="font-causten mb-3">Company</h5>
                            <ul class="list-unstyled">
                                <li><a href="/about" class="text-muted text-decoration-none font-roboto-serif">About</a></li>
                                <li><a href="/careers" class="text-muted text-decoration-none font-roboto-serif">Careers</a></li>
                                <li><a href="/contact" class="text-muted text-decoration-none font-roboto-serif">Contact</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-2 col-md-6 mb-4">
                            <h5 class="font-causten mb-3">Support</h5>
                            <ul class="list-unstyled">
                                <li><a href="/help" class="text-muted text-decoration-none font-roboto-serif">Help Center</a></li>
                                <li><a href="/docs" class="text-muted text-decoration-none font-roboto-serif">Documentation</a></li>
                                <li><a href="/status" class="text-muted text-decoration-none font-roboto-serif">Status</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-2 col-md-6 mb-4">
                            <h5 class="font-causten mb-3">Legal</h5>
                            <ul class="list-unstyled">
                                <li><a href="/privacy" class="text-muted text-decoration-none font-roboto-serif">Privacy</a></li>
                                <li><a href="/terms" class="text-muted text-decoration-none font-roboto-serif">Terms</a></li>
                                <li><a href="/security" class="text-muted text-decoration-none font-roboto-serif">Security</a></li>
                            </ul>
                        </div>
                    </div>
                    <hr class="my-4">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <p class="font-roboto-serif text-muted mb-0">
                                © 2024 foodXchange. All rights reserved.
                            </p>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <div class="d-flex gap-3 justify-content-md-end">
                                <a href="#" class="text-muted"><i class="bi bi-twitter fs-5"></i></a>
                                <a href="#" class="text-muted"><i class="bi bi-linkedin fs-5"></i></a>
                                <a href="#" class="text-muted"><i class="bi bi-facebook fs-5"></i></a>
                            </div>
                        </div>
                    </div>
                </div>
            </footer>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Landing page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Landing Page Error</title></head>
            <body>
                <h1>Landing Page Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard">Back to Dashboard</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    """Login page - Bootstrap styled"""
    try:
        error = request.query_params.get("error", "")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login - foodXchange</title>
            
            <!-- Comprehensive Favicon Setup -->
            <link rel="icon" type="image/png" sizes="32x32" href="/static/brand/logos/Favicon.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/static/brand/logos/Favicon.png">
            <link rel="shortcut icon" href="/static/brand/logos/Favicon.png">
            <link rel="apple-touch-icon" href="/static/brand/logos/Favicon.png">
            <link rel="icon" href="/favicon.ico">
            
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
            <style>
                .login-section {{
                    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                }}
                .login-card {{
                    background: white;
                    border-radius: 1rem;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                .login-logo {{
                    max-height: 60px;
                }}
            </style>
        </head>
        <body>
            <div class="login-section">
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-lg-5 col-md-7">
                            <div class="login-card p-5">
                                <div class="text-center mb-4">
                                    <div class="d-flex align-items-center justify-content-center mb-3">
                                        <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                                             alt="foodXchange" class="login-logo me-2">
                                        <span class="font-causten fw-bold fs-3">foodXchange</span>
                                    </div>
                                    <h2 class="font-causten mb-2">Welcome Back</h2>
                                    <p class="font-roboto-serif text-muted">Sign in to your account</p>
                                </div>

                                {f'<div class="alert alert-danger font-roboto-serif" role="alert">{error}</div>' if error else ''}

                                <form method="POST" action="/login">
                                    <div class="mb-3">
                                        <label for="email" class="form-label font-causten">Email Address</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="bi bi-envelope"></i>
                                            </span>
                                            <input type="email" class="form-control font-roboto-serif" id="email" name="email" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="password" class="form-label font-causten">Password</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="bi bi-lock"></i>
                                            </span>
                                            <input type="password" class="form-control font-roboto-serif" id="password" name="password" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3 form-check">
                                        <input type="checkbox" class="form-check-input" id="remember" name="remember">
                                        <label class="form-check-label font-roboto-serif" for="remember">
                                            Remember me
                                        </label>
                                    </div>
                                    
                                    <div class="d-grid mb-3">
                                        <button type="submit" class="btn btn-primary btn-lg font-causten">
                                            <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
                                        </button>
                                    </div>
                                    
                                    <div class="text-center">
                                        <p class="font-roboto-serif text-muted mb-0">
                                            Don't have an account? 
                                            <a href="/register" class="text-decoration-none font-causten">Sign up</a>
                                        </p>
                                    </div>
                                </form>
                                
                                <hr class="my-4">
                                
                                <div class="text-center">
                                    <a href="/" class="btn btn-outline-secondary font-causten">
                                        <i class="bi bi-arrow-left me-2"></i>Back to Home
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Login page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Login Error</title></head>
            <body>
                <h1>Login Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/">Back to Home</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    """Register page - Bootstrap styled"""
    try:
        error = request.query_params.get("error", "")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Register - foodXchange</title>
            
            <!-- Comprehensive Favicon Setup -->
            <link rel="icon" type="image/png" sizes="32x32" href="/static/brand/logos/Favicon.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/static/brand/logos/Favicon.png">
            <link rel="shortcut icon" href="/static/brand/logos/Favicon.png">
            <link rel="apple-touch-icon" href="/static/brand/logos/Favicon.png">
            <link rel="icon" href="/favicon.ico">
            
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
            <style>
                .register-section {
                    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                }
                .register-card {
                    background: white;
                    border-radius: 1rem;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }
                .register-logo {
                    max-height: 60px;
                }
            </style>
        </head>
        <body>
            <div class="register-section">
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-lg-6 col-md-8">
                            <div class="register-card p-5">
                                <div class="text-center mb-4">
                                    <div class="d-flex align-items-center justify-content-center mb-3">
                                        <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                                             alt="foodXchange" class="register-logo me-2">
                                        <span class="font-causten fw-bold fs-3">foodXchange</span>
                                    </div>
                                    <h2 class="font-causten mb-2">Create Account</h2>
                                    <p class="font-roboto-serif text-muted">Join the food supply chain revolution</p>
                                </div>

                                {f'<div class="alert alert-danger font-roboto-serif" role="alert">{error}</div>' if error else ''}

                                <form method="POST" action="/register">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label for="first_name" class="form-label font-causten">First Name</label>
                                            <input type="text" class="form-control font-roboto-serif" id="first_name" name="first_name" required>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label for="last_name" class="form-label font-causten">Last Name</label>
                                            <input type="text" class="form-control font-roboto-serif" id="last_name" name="last_name" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="email" class="form-label font-causten">Email Address</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="bi bi-envelope"></i>
                                            </span>
                                            <input type="email" class="form-control font-roboto-serif" id="email" name="email" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="company_name" class="form-label font-causten">Company Name</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="bi bi-building"></i>
                                            </span>
                                            <input type="text" class="form-control font-roboto-serif" id="company_name" name="company_name" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="password" class="form-label font-causten">Password</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="bi bi-lock"></i>
                                            </span>
                                            <input type="password" class="form-control font-roboto-serif" id="password" name="password" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="confirm_password" class="form-label font-causten">Confirm Password</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="bi bi-lock-fill"></i>
                                            </span>
                                            <input type="password" class="form-control font-roboto-serif" id="confirm_password" name="confirm_password" required>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3 form-check">
                                        <input type="checkbox" class="form-check-input" id="terms" name="terms" required>
                                        <label class="form-check-label font-roboto-serif" for="terms">
                                            I agree to the <a href="/terms" class="text-decoration-none">Terms of Service</a> and <a href="/privacy" class="text-decoration-none">Privacy Policy</a>
                                        </label>
                                    </div>
                                    
                                    <div class="d-grid mb-3">
                                        <button type="submit" class="btn btn-primary btn-lg font-causten">
                                            <i class="bi bi-person-plus me-2"></i>Create Account
                                        </button>
                                    </div>
                                    
                                    <div class="text-center">
                                        <p class="font-roboto-serif text-muted mb-0">
                                            Already have an account? 
                                            <a href="/login" class="text-decoration-none font-causten">Sign in</a>
                                        </p>
                                    </div>
                                </form>
                                
                                <hr class="my-4">
                                
                                <div class="text-center">
                                    <a href="/" class="btn btn-outline-secondary font-causten">
                                        <i class="bi bi-arrow-left me-2"></i>Back to Home
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Register page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Register Error</title></head>
            <body>
                <h1>Register Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/">Back to Home</a>
            </body>
        </html>
        """, status_code=500)

# Health Endpoints
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/simple")
async def health_simple():
    """Simple health check for basic uptime monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/health/detailed")
async def health_detailed():
    """Detailed health check with system information"""
    try:
        # Test database connection
        from foodxchange.database import get_db
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "application": "healthy",
        "version": "1.0.0"
    }

@app.get("/health/advanced")
async def health_advanced():
    """Advanced health check with comprehensive system status"""
    try:
        # Test database connection
        from foodxchange.database import get_db
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_version_result = db.execute(text("SELECT version()"))
        db_version = db_version_result.fetchone()[0]
        table_count_result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
        table_count = table_count_result.fetchone()[0]
        db_status = {
            "status": "healthy",
            "version": db_version,
            "tables": table_count,
            "connection": "ok"
        }
    except Exception as e:
        db_status = {
            "status": "unhealthy",
            "error": str(e),
            "connection": "failed"
        }

    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent
    }

    app_status = "healthy"
    overall_status = "healthy" if db_status["status"] == "healthy" and app_status == "healthy" else "unhealthy"

    response = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "service": "FoodXchange",
        "version": "1.0.0",
        "environment": os.getenv('FLASK_ENV', 'production'),
        "services": {
            "database": db_status,
            "application": app_status
        },
        "system": system_info,
        "monitoring": {
            "sentry": "configured" if os.getenv('SENTRY_DSN') else "not_configured",
            "uptimerobot": "configured" if os.path.exists('uptimerobot_config.json') else "not_configured",
            "azure_monitor": azure_monitor.get_status() if azure_monitor else {"enabled": False, "error": "not_available"}
        }
    }
    return response

@app.get("/health/enhanced")
async def enhanced_health():
    """Enhanced health check with detailed monitoring"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application metrics
        process = psutil.Process()
        process_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Database health check
        try:
            from foodxchange.database import get_db
            from sqlalchemy import text
            db = next(get_db())
            db.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            sentry_sdk.capture_exception(e)
        
        # Add metrics to Sentry
        sentry_sdk.set_tag("health_check_cpu_percent", cpu_percent)
        sentry_sdk.set_tag("health_check_memory_percent", memory.percent)
        sentry_sdk.set_tag("health_check_disk_percent", disk.percent)
        sentry_sdk.set_tag("health_check_process_memory_mb", round(process_memory, 2))
        
        # Set performance context
        sentry_sdk.set_context("system_health", {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "process_memory_mb": round(process_memory, 2),
            "database_status": db_status,
        })
        
        # Determine overall health
        overall_status = "healthy"
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
            overall_status = "warning"
        if db_status != "healthy":
            overall_status = "unhealthy"
        
        response = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "process_memory_mb": round(process_memory, 2),
            },
            "services": {
                "database": db_status,
                "application": "healthy",
            },
            "version": "1.0.0",
            "environment": os.getenv("SENTRY_ENVIRONMENT", "production")
        }
        
        # Report warnings to Sentry
        if overall_status == "warning":
            sentry_sdk.capture_message(
                "System health warning detected",
                level="warning",
                tags={
                    "health_check": True,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                }
            )
        
        return response
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/readiness")
async def health_readiness():
    """Kubernetes readiness probe endpoint"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health/liveness")
async def health_liveness():
    """Kubernetes liveness probe endpoint"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus-style metrics endpoint"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        process = psutil.Process()
        process_memory = process.memory_info().rss / 1024 / 1024
        
        metrics_text = f"""# HELP foodxchange_cpu_percent CPU usage percentage
# TYPE foodxchange_cpu_percent gauge
foodxchange_cpu_percent {cpu_percent}

# HELP foodxchange_memory_percent Memory usage percentage
# TYPE foodxchange_memory_percent gauge
foodxchange_memory_percent {memory.percent}

# HELP foodxchange_disk_percent Disk usage percentage
# TYPE foodxchange_disk_percent gauge
foodxchange_disk_percent {disk.percent}

# HELP foodxchange_process_memory_mb Process memory usage in MB
# TYPE foodxchange_process_memory_mb gauge
foodxchange_process_memory_mb {process_memory}

# HELP foodxchange_uptime_seconds Application uptime in seconds
# TYPE foodxchange_uptime_seconds counter
foodxchange_uptime_seconds {time.time() - start_time}
"""
        
        return Response(content=metrics_text, media_type="text/plain")
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}

@app.get("/test-sentry")
async def test_sentry():
    """Test endpoint to trigger a Sentry error"""
    try:
        # Trigger a test error
        raise ValueError("This is a test error from FoodXchange - Sentry integration test")
    except Exception as e:
        # Capture the error in Sentry
        sentry_sdk.capture_exception(e)
        return {
            "message": "Test error triggered and sent to Sentry",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/sentry-debug")
async def trigger_error():
    """Debug endpoint to verify Sentry integration by triggering a division by zero error"""
    division_by_zero = 1 / 0

@app.get("/monitoring/azure")
async def azure_monitor_status():
    """Get Azure Monitor status and configuration"""
    try:
        if not azure_monitor:
            return {
                "status": "not_available",
                "message": "Azure Monitor service not available",
                "timestamp": datetime.now().isoformat()
            }
        
        status = azure_monitor.get_status()
        
        # Test Azure Monitor functionality
        if azure_monitor.enabled:
            try:
                azure_monitor.log_event("health_check", {
                    "endpoint": "/monitoring/azure",
                    "timestamp": datetime.now().isoformat()
                })
                status["test_event_sent"] = True
            except Exception as e:
                status["test_event_sent"] = False
                status["test_event_error"] = str(e)
        
        return {
            "status": "success",
            "azure_monitor": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get Azure Monitor status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/monitoring/test")
async def test_monitoring():
    """Test all monitoring systems"""
    results = {}
    
    # Test Sentry
    try:
        sentry_sdk.capture_message("Monitoring test from FoodXchange", level="info")
        results["sentry"] = {"status": "success", "message": "Test event sent"}
    except Exception as e:
        results["sentry"] = {"status": "error", "message": str(e)}
    
    # Test Azure Monitor
    if azure_monitor and azure_monitor.enabled:
        try:
            azure_monitor.log_event("monitoring_test", {
                "test_type": "comprehensive",
                "timestamp": datetime.now().isoformat()
            })
            results["azure_monitor"] = {"status": "success", "message": "Test event sent"}
        except Exception as e:
            results["azure_monitor"] = {"status": "error", "message": str(e)}
    else:
        results["azure_monitor"] = {"status": "not_available", "message": "Azure Monitor not configured"}
    
    return {
        "status": "completed",
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

# Application Routes
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        # Simplified dashboard without authentication dependency
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard - foodXchange</title>
            
            <!-- Comprehensive Favicon Setup -->
            <link rel="icon" type="image/png" sizes="32x32" href="/static/brand/logos/Favicon.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/static/brand/logos/Favicon.png">
            <link rel="shortcut icon" href="/static/brand/logos/Favicon.png">
            <link rel="apple-touch-icon" href="/static/brand/logos/Favicon.png">
            <link rel="icon" href="/favicon.ico">
            
            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            
            <!-- Bootstrap Icons -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            
            <!-- Food Xchange Custom Fonts -->
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
            
            <style>
                :root {{
                    --bs-primary: #4A90E2;
                    --bs-secondary: #F97316;
                    --bs-success: #10B981;
                    --bs-info: #4A90E2;
                    --bs-warning: #F97316;
                    --bs-danger: #EF4444;
                    --bs-light: #F8F9FA;
                    --bs-dark: #212529;
                }}
                
                body {{
                    font-family: 'Causten', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: #f8f9fa;
                }}
                
                .sidebar {{
                    background: linear-gradient(135deg, var(--bs-primary) 0%, #357ABD 100%);
                    min-height: 100vh;
                }}
                
                .sidebar .nav-link {{
                    color: rgba(255, 255, 255, 0.8);
                    padding: 0.75rem 1rem;
                    border-radius: 0.375rem;
                    margin: 0.125rem 0;
                }}
                
                .sidebar .nav-link:hover,
                .sidebar .nav-link.active {{
                    color: white;
                    background-color: rgba(255, 255, 255, 0.1);
                }}
                
                .stats-card {{
                    background: linear-gradient(135deg, var(--bs-primary) 0%, #357ABD 100%);
                    color: white;
                }}
                
                .stats-card-secondary {{
                    background: linear-gradient(135deg, var(--bs-secondary) 0%, #E55A2B 100%);
                    color: white;
                }}
                
                .stats-card-success {{
                    background: linear-gradient(135deg, var(--bs-success) 0%, #059669 100%);
                    color: white;
                }}
                
                .stats-card-warning {{
                    background: linear-gradient(135deg, var(--bs-warning) 0%, #E55A2B 100%);
                    color: white;
                }}
            </style>
        </head>
        <body>
            <!-- Navigation -->
            <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm border-bottom">
                <div class="container-fluid">
                    <a class="navbar-brand d-flex align-items-center" href="/">
                        <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" alt="foodXchange" height="32" class="me-2">
                        <span class="text-primary">foodXchange</span>
                    </a>
                    
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                    <i class="bi bi-person-circle me-1"></i>Guest User
                                </a>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="/dashboard"><i class="bi bi-speedometer2 me-2"></i>Dashboard</a></li>
                                    <li><a class="dropdown-item" href="/profile"><i class="bi bi-person me-2"></i>Profile</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item" href="/login"><i class="bi bi-box-arrow-in-right me-2"></i>Login</a></li>
                                    <li><a class="dropdown-item" href="/logout"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>

            <!-- Main Content -->
            <div class="container-fluid">
                <div class="row">
                    <!-- Sidebar -->
                    <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                        <div class="position-sticky pt-3">
                            <ul class="nav flex-column">
                                <li class="nav-item">
                                    <a class="nav-link active" href="/dashboard">
                                        <i class="bi bi-speedometer2"></i>Dashboard
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/rfq/new">
                                        <i class="bi bi-file-earmark-plus"></i>New RFQ
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/rfqs">
                                        <i class="bi bi-file-earmark-text"></i>RFQs
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/orders">
                                        <i class="bi bi-cart"></i>Orders
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/suppliers">
                                        <i class="bi bi-building"></i>Suppliers
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/products">
                                        <i class="bi bi-box"></i>Products
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/quotes">
                                        <i class="bi bi-currency-dollar"></i>Quotes
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/analytics">
                                        <i class="bi bi-graph-up"></i>Analytics
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/projects">
                                        <i class="bi bi-kanban"></i>Projects
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/agent-dashboard">
                                        <i class="bi bi-robot"></i>AI Agent
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </nav>
                    
                    <!-- Main Content Area -->
                    <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                            <h1 class="h2 font-causten">Dashboard</h1>
                            <div class="btn-toolbar mb-2 mb-md-0">
                                <div class="btn-group me-2">
                                    <a href="/rfq/new" class="btn btn-sm btn-primary font-causten">
                                        <i class="bi bi-plus-circle me-1"></i>New RFQ
                                    </a>
                                    <a href="/suppliers/add" class="btn btn-sm btn-outline-primary font-causten">
                                        <i class="bi bi-building-add me-1"></i>Add Supplier
                                    </a>
                                </div>
                            </div>
                        </div>

                        <!-- Stats Cards -->
                        <div class="row g-4 mb-4">
                            <div class="col-xl-3 col-md-6">
                                <div class="card stats-card border-0">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 class="card-title text-white-50 mb-1 font-causten">Total RFQs</h6>
                                                <h3 class="mb-0 text-white font-causten">24</h3>
                                            </div>
                                            <div class="text-white-50">
                                                <i class="bi bi-file-earmark-text display-6"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card stats-card-secondary border-0">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 class="card-title text-white-50 mb-1 font-causten">Active Orders</h6>
                                                <h3 class="mb-0 text-white font-causten">12</h3>
                                            </div>
                                            <div class="text-white-50">
                                                <i class="bi bi-cart-check display-6"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card stats-card-success border-0">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 class="card-title text-white-50 mb-1 font-causten">Suppliers</h6>
                                                <h3 class="mb-0 text-white font-causten">89</h3>
                                            </div>
                                            <div class="text-white-50">
                                                <i class="bi bi-building display-6"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-xl-3 col-md-6">
                                <div class="card stats-card-warning border-0">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 class="card-title text-white-50 mb-1 font-causten">Pending Quotes</h6>
                                                <h3 class="mb-0 text-white font-causten">7</h3>
                                            </div>
                                            <div class="text-white-50">
                                                <i class="bi bi-currency-dollar display-6"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Recent Activity and Quick Actions -->
                        <div class="row g-4">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-clock-history me-2"></i>Recent Activity
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="list-group list-group-flush">
                                            <div class="list-group-item border-0 px-0">
                                                <div class="d-flex align-items-center">
                                                    <div class="flex-shrink-0">
                                                        <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                                            <i class="bi bi-file-earmark-plus text-white"></i>
                                                        </div>
                                                    </div>
                                                    <div class="flex-grow-1 ms-3">
                                                        <h6 class="mb-1 font-causten">New RFQ Created</h6>
                                                        <p class="mb-1 text-muted font-roboto-serif">Organic rice procurement for ABC Restaurant</p>
                                                        <small class="text-muted font-roboto-serif">2 hours ago</small>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="list-group-item border-0 px-0">
                                                <div class="d-flex align-items-center">
                                                    <div class="flex-shrink-0">
                                                        <div class="bg-success rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                                            <i class="bi bi-check-circle text-white"></i>
                                                        </div>
                                                    </div>
                                                    <div class="flex-grow-1 ms-3">
                                                        <h6 class="mb-1 font-causten">Order Confirmed</h6>
                                                        <p class="mb-1 text-muted font-roboto-serif">Order #ORD-2024-001 has been confirmed</p>
                                                        <small class="text-muted font-roboto-serif">4 hours ago</small>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="list-group-item border-0 px-0">
                                                <div class="d-flex align-items-center">
                                                    <div class="flex-shrink-0">
                                                        <div class="bg-warning rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                                            <i class="bi bi-building text-white"></i>
                                                        </div>
                                                    </div>
                                                    <div class="flex-grow-1 ms-3">
                                                        <h6 class="mb-1 font-causten">New Supplier Registered</h6>
                                                        <p class="mb-1 text-muted font-roboto-serif">Fresh Foods Co. joined the platform</p>
                                                        <small class="text-muted font-roboto-serif">1 day ago</small>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-lg-4">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-lightning me-2"></i>Quick Actions
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-grid gap-2">
                                            <a href="/rfq/new" class="btn btn-primary font-causten">
                                                <i class="bi bi-file-earmark-plus me-2"></i>Create RFQ
                                            </a>
                                            <a href="/suppliers/add" class="btn btn-outline-primary font-causten">
                                                <i class="bi bi-building-add me-2"></i>Add Supplier
                                            </a>
                                            <a href="/orders" class="btn btn-outline-success font-causten">
                                                <i class="bi bi-cart me-2"></i>View Orders
                                            </a>
                                            <a href="/analytics" class="btn btn-outline-info font-causten">
                                                <i class="bi bi-graph-up me-2"></i>Analytics
                                            </a>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="card border-0 shadow-sm mt-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-calendar-event me-2"></i>Upcoming Deadlines
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="list-group list-group-flush">
                                            <div class="list-group-item border-0 px-0">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <h6 class="mb-1 font-causten">RFQ #RFQ-2024-015</h6>
                                                        <small class="text-muted font-roboto-serif">Organic vegetables</small>
                                                    </div>
                                                    <span class="badge bg-warning font-roboto-serif">Tomorrow</span>
                                                </div>
                                            </div>
                                            <div class="list-group-item border-0 px-0">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <h6 class="mb-1 font-causten">Order #ORD-2024-008</h6>
                                                        <small class="text-muted font-roboto-serif">Dairy products</small>
                                                    </div>
                                                    <span class="badge bg-info font-roboto-serif">3 days</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </main>
                </div>
            </div>

            <!-- Footer -->
            <footer class="bg-light border-top mt-5">
                <div class="container py-4">
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="text-primary font-causten">foodXchange</h5>
                            <p class="text-muted font-roboto-serif">B2B Food Marketplace Platform</p>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <p class="text-muted font-roboto-serif">&copy; 2024 foodXchange. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </footer>

            <!-- Bootstrap JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Dashboard Error</title></head>
            <body>
                <h1>Dashboard Error</h1>
                <p>Error: {str(e)}</p>
                <p>Type: {type(e).__name__}</p>
                <a href="/">Go Home</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/suppliers", response_class=HTMLResponse, name="suppliers_list")
async def suppliers_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    suppliers = [
        {"id": 1, "name": "Mediterranean Delights", "location": "Greece", "products": ["Olive Oil", "Feta Cheese"], "status": "active"},
        {"id": 2, "name": "Italian Fine Foods", "location": "Italy", "products": ["Pasta", "Tomatoes"], "status": "active"},
        {"id": 3, "name": "Spanish Imports Co", "location": "Spain", "products": ["Jamón", "Manchego"], "status": "pending"}
    ]
    return templates.TemplateResponse("suppliers.html", {"request": request, "suppliers": suppliers, "current_user": user})

@app.get("/suppliers/add", response_class=HTMLResponse, name="add_supplier")
async def add_supplier(request: Request):
    """Add new supplier page - Bootstrap styled"""
    try:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Add Supplier - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Add New Supplier</h1>
                                <p class="text-muted mb-0 font-roboto-serif">Add a new supplier to your network</p>
                            </div>
                            <div class="btn-group">
                                <a href="/suppliers" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Suppliers
                                </a>
                            </div>
                        </div>

                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-plus-circle me-2"></i>Supplier Information
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <form onsubmit="submitSupplier(event)">
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierName" class="form-label font-causten">Company Name *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierName" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierStatus" class="form-label font-causten">Status *</label>
                                                    <select class="form-select font-roboto-serif" id="supplierStatus" required>
                                                        <option value="">Select Status</option>
                                                        <option value="Active">Active</option>
                                                        <option value="Inactive">Inactive</option>
                                                        <option value="Pending">Pending</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="contactPerson" class="form-label font-causten">Contact Person *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="contactPerson" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierEmail" class="form-label font-causten">Email *</label>
                                                    <input type="email" class="form-control font-roboto-serif" id="supplierEmail" required>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierPhone" class="form-label font-causten">Phone *</label>
                                                    <input type="tel" class="form-control font-roboto-serif" id="supplierPhone" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierCountry" class="form-label font-causten">Country *</label>
                                                    <select class="form-select font-roboto-serif" id="supplierCountry" required>
                                                        <option value="">Select Country</option>
                                                        <option value="United States">United States</option>
                                                        <option value="Canada">Canada</option>
                                                        <option value="Mexico">Mexico</option>
                                                        <option value="United Kingdom">United Kingdom</option>
                                                        <option value="Germany">Germany</option>
                                                        <option value="France">France</option>
                                                        <option value="Italy">Italy</option>
                                                        <option value="Spain">Spain</option>
                                                        <option value="China">China</option>
                                                        <option value="Japan">Japan</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierAddress" class="form-label font-causten">Address *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierAddress" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierCity" class="form-label font-causten">City *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierCity" required>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-4 mb-3">
                                                    <label for="supplierState" class="form-label font-causten">State/Province *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierState" required>
                                                </div>
                                                <div class="col-md-4 mb-3">
                                                    <label for="supplierZip" class="form-label font-causten">ZIP/Postal Code *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierZip" required>
                                                </div>
                                                <div class="col-md-4 mb-3">
                                                    <label for="paymentTerms" class="form-label font-causten">Payment Terms</label>
                                                    <select class="form-select font-roboto-serif" id="paymentTerms">
                                                        <option value="">Select Payment Terms</option>
                                                        <option value="Net 30">Net 30</option>
                                                        <option value="Net 15">Net 15</option>
                                                        <option value="Net 60">Net 60</option>
                                                        <option value="Due on Receipt">Due on Receipt</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="mb-3">
                                                <label for="deliveryTime" class="form-label font-causten">Delivery Time</label>
                                                <input type="text" class="form-control font-roboto-serif" id="deliveryTime" placeholder="e.g., 3-5 business days">
                                            </div>
                                            
                                            <div class="mb-3">
                                                <label for="supplierDescription" class="form-label font-causten">Description</label>
                                                <textarea class="form-control font-roboto-serif" id="supplierDescription" rows="3" placeholder="Enter supplier description..."></textarea>
                                            </div>
                                            
                                            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                                <button type="button" class="btn btn-outline-secondary font-causten" onclick="window.location.href='/suppliers'">
                                                    Cancel
                                                </button>
                                                <button type="submit" class="btn btn-primary font-causten">
                                                    <i class="bi bi-plus-circle me-2"></i>Add Supplier
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                function submitSupplier(event) {
                    event.preventDefault();
                    
                    const formData = {
                        name: document.getElementById('supplierName').value,
                        status: document.getElementById('supplierStatus').value,
                        contact_person: document.getElementById('contactPerson').value,
                        email: document.getElementById('supplierEmail').value,
                        phone: document.getElementById('supplierPhone').value,
                        country: document.getElementById('supplierCountry').value,
                        address: document.getElementById('supplierAddress').value,
                        city: document.getElementById('supplierCity').value,
                        state: document.getElementById('supplierState').value,
                        zip_code: document.getElementById('supplierZip').value,
                        payment_terms: document.getElementById('paymentTerms').value,
                        delivery_time: document.getElementById('deliveryTime').value,
                        description: document.getElementById('supplierDescription').value
                    };
                    
                    // Simulate form submission
                    alert('Supplier added successfully!');
                    console.log('Supplier data:', formData);
                    
                    // Redirect to suppliers list
                    setTimeout(() => {
                        window.location.href = '/suppliers';
                    }, 1000);
                }
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Add supplier page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Add Supplier Error</title></head>
            <body>
                <h1>Add Supplier Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/suppliers">Back to Suppliers</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/suppliers/{supplier_id}", response_class=HTMLResponse, name="view_supplier")
async def view_supplier(request: Request, supplier_id: int):
    """View supplier details page - Bootstrap styled"""
    try:
        supplier = {
            "id": supplier_id,
            "name": "Mediterranean Delights",
            "contact_person": "Maria Rodriguez",
            "email": "maria@mediterraneandelights.com",
            "phone": "+1 (555) 123-4567",
            "address": "789 Supplier Street, Miami, FL 33101",
            "country": "United States",
            "rating": 4.8,
            "products_count": 45,
            "orders_count": 12,
            "total_spend": 125000,
            "status": "Active",
            "joined_date": "2023-06-15",
            "certifications": ["Organic", "ISO 9001", "HACCP"],
            "payment_terms": "Net 30",
            "delivery_time": "3-5 business days"
        }
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Supplier Details - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Supplier Details</h1>
                                <p class="text-muted mb-0 font-roboto-serif">#{supplier_id} - {supplier['name']}</p>
                            </div>
                            <div class="btn-group">
                                <a href="/suppliers" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Suppliers
                                </a>
                                <button type="button" class="btn btn-primary font-causten" onclick="editSupplier({supplier_id})">
                                    <i class="bi bi-pencil me-2"></i>Edit Supplier
                                </button>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-building me-2"></i>Supplier Information
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Company Name</label>
                                                <div class="font-causten fw-bold">{supplier['name']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Status</label>
                                                <div>
                                                    <span class="badge bg-success font-causten">{supplier['status']}</span>
                                                </div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Contact Person</label>
                                                <div class="font-causten fw-bold">{supplier['contact_person']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Email</label>
                                                <div class="font-causten">{supplier['email']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Phone</label>
                                                <div class="font-causten">{supplier['phone']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Country</label>
                                                <div class="font-causten">{supplier['country']}</div>
                                            </div>
                                            <div class="col-12 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Address</label>
                                                <div class="font-roboto-serif">{supplier['address']}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-lg-4">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-lightning me-2"></i>Quick Actions
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-grid gap-2">
                                            <button type="button" class="btn btn-outline-primary font-causten" onclick="editSupplier({supplier_id})">
                                                <i class="bi bi-pencil me-2"></i>Edit Supplier
                                            </button>
                                            <button type="button" class="btn btn-outline-success font-causten" onclick="createRFQ({supplier_id})">
                                                <i class="bi bi-file-earmark-plus me-2"></i>Create RFQ
                                            </button>
                                            <button type="button" class="btn btn-outline-danger font-causten" onclick="deleteSupplier({supplier_id})">
                                                <i class="bi bi-trash me-2"></i>Delete Supplier
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                function editSupplier(supplierId) {
                    alert(`Editing supplier ${supplierId}...`);
                }
                
                function createRFQ(supplierId) {
                    alert(`Creating RFQ for supplier ${supplierId}...`);
                }
                
                function deleteSupplier(supplierId) {
                    if (confirm(`Are you sure you want to delete supplier ${supplierId}?`)) {
                        alert(`Supplier ${supplierId} deleted successfully!`);
                        window.location.href = '/suppliers';
                    }
                }
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"View supplier page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Supplier Details Error</title></head>
            <body>
                <h1>Supplier Details Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/suppliers">Back to Suppliers</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/suppliers/{supplier_id}/edit", response_class=HTMLResponse, name="edit_supplier")
async def edit_supplier(request: Request, supplier_id: int):
    """Edit supplier page - Bootstrap styled"""
    try:
        supplier = {
            "id": supplier_id,
            "name": "Mediterranean Delights",
            "contact_person": "Maria Rodriguez",
            "email": "maria@mediterraneandelights.com",
            "phone": "+1 (555) 123-4567",
            "address": "789 Supplier Street",
            "city": "Miami",
            "state": "FL",
            "zip_code": "33101",
            "country": "United States",
            "status": "Active",
            "payment_terms": "Net 30",
            "delivery_time": "3-5 business days"
        }
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Edit Supplier - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Edit Supplier</h1>
                                <p class="text-muted mb-0 font-roboto-serif">#{supplier_id} - {supplier['name']}</p>
                            </div>
                            <div class="btn-group">
                                <a href="/suppliers/{supplier_id}" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Supplier
                                </a>
                            </div>
                        </div>

                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-pencil me-2"></i>Edit Supplier Information
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <form onsubmit="updateSupplier(event)">
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierName" class="form-label font-causten">Company Name *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierName" value="{supplier['name']}" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierStatus" class="form-label font-causten">Status *</label>
                                                    <select class="form-select font-roboto-serif" id="supplierStatus" required>
                                                        <option value="Active" {'selected' if supplier['status'] == 'Active' else ''}>Active</option>
                                                        <option value="Inactive" {'selected' if supplier['status'] == 'Inactive' else ''}>Inactive</option>
                                                        <option value="Pending" {'selected' if supplier['status'] == 'Pending' else ''}>Pending</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="contactPerson" class="form-label font-causten">Contact Person *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="contactPerson" value="{supplier['contact_person']}" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierEmail" class="form-label font-causten">Email *</label>
                                                    <input type="email" class="form-control font-roboto-serif" id="supplierEmail" value="{supplier['email']}" required>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierPhone" class="form-label font-causten">Phone *</label>
                                                    <input type="tel" class="form-control font-roboto-serif" id="supplierPhone" value="{supplier['phone']}" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierCountry" class="form-label font-causten">Country *</label>
                                                    <select class="form-select font-roboto-serif" id="supplierCountry" required>
                                                        <option value="United States" {'selected' if supplier['country'] == 'United States' else ''}>United States</option>
                                                        <option value="Canada" {'selected' if supplier['country'] == 'Canada' else ''}>Canada</option>
                                                        <option value="Mexico" {'selected' if supplier['country'] == 'Mexico' else ''}>Mexico</option>
                                                        <option value="United Kingdom" {'selected' if supplier['country'] == 'United Kingdom' else ''}>United Kingdom</option>
                                                        <option value="Germany" {'selected' if supplier['country'] == 'Germany' else ''}>Germany</option>
                                                        <option value="France" {'selected' if supplier['country'] == 'France' else ''}>France</option>
                                                        <option value="Italy" {'selected' if supplier['country'] == 'Italy' else ''}>Italy</option>
                                                        <option value="Spain" {'selected' if supplier['country'] == 'Spain' else ''}>Spain</option>
                                                        <option value="China" {'selected' if supplier['country'] == 'China' else ''}>China</option>
                                                        <option value="Japan" {'selected' if supplier['country'] == 'Japan' else ''}>Japan</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierAddress" class="form-label font-causten">Address *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierAddress" value="{supplier['address']}" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="supplierCity" class="form-label font-causten">City *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierCity" value="{supplier['city']}" required>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-4 mb-3">
                                                    <label for="supplierState" class="form-label font-causten">State/Province *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierState" value="{supplier['state']}" required>
                                                </div>
                                                <div class="col-md-4 mb-3">
                                                    <label for="supplierZip" class="form-label font-causten">ZIP/Postal Code *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="supplierZip" value="{supplier['zip_code']}" required>
                                                </div>
                                                <div class="col-md-4 mb-3">
                                                    <label for="paymentTerms" class="form-label font-causten">Payment Terms</label>
                                                    <select class="form-select font-roboto-serif" id="paymentTerms">
                                                        <option value="Net 30" {'selected' if supplier['payment_terms'] == 'Net 30' else ''}>Net 30</option>
                                                        <option value="Net 15" {'selected' if supplier['payment_terms'] == 'Net 15' else ''}>Net 15</option>
                                                        <option value="Net 60" {'selected' if supplier['payment_terms'] == 'Net 60' else ''}>Net 60</option>
                                                        <option value="Due on Receipt" {'selected' if supplier['payment_terms'] == 'Due on Receipt' else ''}>Due on Receipt</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="mb-3">
                                                <label for="deliveryTime" class="form-label font-causten">Delivery Time</label>
                                                <input type="text" class="form-control font-roboto-serif" id="deliveryTime" value="{supplier['delivery_time']}" placeholder="e.g., 3-5 business days">
                                            </div>
                                            
                                            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                                <button type="button" class="btn btn-outline-secondary font-causten" onclick="window.location.href='/suppliers/{supplier_id}'">
                                                    Cancel
                                                </button>
                                                <button type="submit" class="btn btn-primary font-causten">
                                                    <i class="bi bi-check-circle me-2"></i>Update Supplier
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                function updateSupplier(event) {
                    event.preventDefault();
                    
                    const formData = {
                        id: {supplier_id},
                        name: document.getElementById('supplierName').value,
                        status: document.getElementById('supplierStatus').value,
                        contact_person: document.getElementById('contactPerson').value,
                        email: document.getElementById('supplierEmail').value,
                        phone: document.getElementById('supplierPhone').value,
                        country: document.getElementById('supplierCountry').value,
                        address: document.getElementById('supplierAddress').value,
                        city: document.getElementById('supplierCity').value,
                        state: document.getElementById('supplierState').value,
                        zip_code: document.getElementById('supplierZip').value,
                        payment_terms: document.getElementById('paymentTerms').value,
                        delivery_time: document.getElementById('deliveryTime').value
                    };
                    
                    // Simulate form submission
                    alert('Supplier updated successfully!');
                    console.log('Supplier data:', formData);
                    
                    // Redirect to supplier details
                    setTimeout(() => {
                        window.location.href = '/suppliers/{supplier_id}';
                    }, 1000);
                }
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Edit supplier page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Edit Supplier Error</title></head>
            <body>
                <h1>Edit Supplier Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/suppliers/{supplier_id}">Back to Supplier</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/rfq/new", response_class=HTMLResponse, name="new_rfq")
async def new_rfq(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("rfq_new.html", {"request": request, "current_user": user})

@app.post("/rfq/new", response_class=HTMLResponse)
async def create_rfq(request: Request, product: str = Form(...), quantity: int = Form(...), deadline: str = Form(...), notes: str = Form(None), db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Placeholder: Save RFQ to database
    # Redirect to dashboard or show confirmation
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": {"suppliers": 0, "rfqs": 1, "quotes": 0, "emails": 0}, "message": "RFQ created!", "current_user": user})

@app.get("/orders", response_class=HTMLResponse, name="orders_list")
async def orders_list(request: Request, db: Session = Depends(get_db)):
    try:
        user = get_current_user_context(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Return a complete HTML orders page directly
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orders - foodXchange</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Orders</h1>
                                <p class="text-muted mb-0 font-roboto-serif">Manage your purchase orders and track deliveries</p>
                            </div>
                            <a href="/rfq/new" class="btn btn-primary font-causten">
                                <i class="bi bi-plus-circle me-2"></i>New Order
                            </a>
                        </div>

                        <div class="card border-0 shadow-sm">
                            <div class="card-header bg-white">
                                <h5 class="card-title mb-0 font-causten">Your Orders</h5>
                            </div>
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-hover mb-0">
                                        <thead class="table-light">
                                            <tr>
                                                <th class="border-0 font-causten">Order Number</th>
                                                <th class="border-0 font-causten">Product</th>
                                                <th class="border-0 font-causten">Quantity</th>
                                                <th class="border-0 font-causten">Supplier</th>
                                                <th class="border-0 font-causten">Total</th>
                                                <th class="border-0 font-causten">Status</th>
                                                <th class="border-0 font-causten">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <div class="fw-bold font-causten">ORD-2024-001</div>
                                                    <small class="text-muted font-roboto-serif">2024-01-15</small>
                                                </td>
                                                <td>
                                                    <div class="fw-bold font-causten">Organic Rice</div>
                                                    <small class="text-muted font-roboto-serif">Grains</small>
                                                </td>
                                                <td class="font-roboto-serif">1000 kg</td>
                                                <td class="font-roboto-serif">Mediterranean Delights</td>
                                                <td class="font-roboto-serif">$2,500</td>
                                                <td>
                                                    <span class="badge bg-success font-causten">Delivered</span>
                                                </td>
                                                <td>
                                                    <div class="btn-group" role="group">
                                                        <a href="/orders/1" class="btn btn-sm btn-outline-primary font-causten">
                                                            <i class="bi bi-eye me-1"></i>View
                                                        </a>
                                                        <a href="/orders/1/edit" class="btn btn-sm btn-outline-secondary font-causten">
                                                            <i class="bi bi-pencil me-1"></i>Edit
                                                        </a>
                                                    </div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <div class="fw-bold font-causten">ORD-2024-002</div>
                                                    <small class="text-muted font-roboto-serif">2024-01-16</small>
                                                </td>
                                                <td>
                                                    <div class="fw-bold font-causten">Fresh Vegetables</div>
                                                    <small class="text-muted font-roboto-serif">Produce</small>
                                                </td>
                                                <td class="font-roboto-serif">500 kg</td>
                                                <td class="font-roboto-serif">Italian Fine Foods</td>
                                                <td class="font-roboto-serif">$1,800</td>
                                                <td>
                                                    <span class="badge bg-warning font-causten">In Transit</span>
                                                </td>
                                                <td>
                                                    <div class="btn-group" role="group">
                                                        <a href="/orders/2" class="btn btn-sm btn-outline-primary font-causten">
                                                            <i class="bi bi-eye me-1"></i>View
                                                        </a>
                                                        <a href="/orders/2/edit" class="btn btn-sm btn-outline-secondary font-causten">
                                                            <i class="bi bi-pencil me-1"></i>Edit
                                                        </a>
                                                    </div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <div class="fw-bold font-causten">ORD-2024-003</div>
                                                    <small class="text-muted font-roboto-serif">2024-01-17</small>
                                                </td>
                                                <td>
                                                    <div class="fw-bold font-causten">Dairy Products</div>
                                                    <small class="text-muted font-roboto-serif">Dairy</small>
                                                </td>
                                                <td class="font-roboto-serif">200 kg</td>
                                                <td class="font-roboto-serif">Spanish Imports Co</td>
                                                <td class="font-roboto-serif">$900</td>
                                                <td>
                                                    <span class="badge bg-info font-causten">Processing</span>
                                                </td>
                                                <td>
                                                    <div class="btn-group" role="group">
                                                        <a href="/orders/3" class="btn btn-sm btn-outline-primary font-causten">
                                                            <i class="bi bi-eye me-1"></i>View
                                                        </a>
                                                        <a href="/orders/3/edit" class="btn btn-sm btn-outline-secondary font-causten">
                                                            <i class="bi bi-pencil me-1"></i>Edit
                                                        </a>
                                                    </div>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Orders page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Orders Error</title></head>
            <body>
                <h1>Orders Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard">Back to Dashboard</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/orders/{order_id}/edit", response_class=HTMLResponse, name="edit_order")
async def edit_order(request: Request, order_id: int, db: Session = Depends(get_db)):
    try:
        user = get_current_user_context(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Return a simple edit order page
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Edit Order - foodXchange</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card shadow">
                            <div class="card-header bg-primary text-white">
                                <h4 class="mb-0 font-causten">
                                    <i class="bi bi-pencil-square me-2"></i>Edit Order #{order_id}
                                </h4>
                            </div>
                            <div class="card-body">
                                <form>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label font-causten">Order Number</label>
                                            <input type="text" class="form-control font-roboto-serif" value="ORD-2024-{order_id:03d}" readonly>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label font-causten">Status</label>
                                            <select class="form-select font-roboto-serif">
                                                <option>Pending</option>
                                                <option>Processing</option>
                                                <option selected>Delivered</option>
                                                <option>Cancelled</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label font-causten">Product</label>
                                            <input type="text" class="form-control font-roboto-serif" value="Organic Rice">
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label font-causten">Quantity</label>
                                            <input type="number" class="form-control font-roboto-serif" value="1000">
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label font-causten">Notes</label>
                                        <textarea class="form-control font-roboto-serif" rows="3"></textarea>
                                    </div>
                                    <div class="d-flex justify-content-end gap-2">
                                        <a href="/orders" class="btn btn-outline-secondary font-causten">Cancel</a>
                                        <button type="submit" class="btn btn-primary font-causten">Update Order</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Edit order page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Edit Order Error</title></head>
            <body>
                <h1>Edit Order Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/orders">Back to Orders</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/orders/{order_id}/invoice", response_class=HTMLResponse, name="order_invoice")
async def order_invoice(request: Request, order_id: int, db: Session = Depends(get_db)):
    try:
        user = get_current_user_context(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Return a complete HTML invoice page directly
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invoice - Order #{order_id} - foodXchange</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
            <style>
                @media print {{
                    .no-print {{ display: none !important; }}
                    .invoice-container {{ 
                        max-width: 100% !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }}
                    body {{ 
                        background: white !important;
                        font-size: 12px !important;
                    }}
                    .card {{ 
                        border: none !important;
                        box-shadow: none !important;
                    }}
                }}
                .invoice-header {{
                    background: linear-gradient(135deg, var(--bs-primary) 0%, #357ABD 100%);
                    color: white;
                    padding: 2rem;
                    border-radius: 0.5rem 0.5rem 0 0;
                }}
                .invoice-number {{
                    font-size: 1.5rem;
                    font-weight: bold;
                }}
                .company-logo {{
                    max-height: 60px;
                }}
                .invoice-details {{
                    background-color: #f8f9fa;
                    padding: 1.5rem;
                }}
                .total-section {{
                    background-color: #e9ecef;
                    padding: 1rem;
                    border-radius: 0 0 0.5rem 0.5rem;
                }}
                .signature-line {{
                    border-top: 1px solid #dee2e6;
                    margin-top: 2rem;
                    padding-top: 1rem;
                }}
            </style>
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row justify-content-center">
                    <div class="col-lg-10">
                        <!-- Print Controls -->
                        <div class="no-print mb-4">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <a href="/orders/{order_id}" class="btn btn-outline-secondary font-causten">
                                        <i class="bi bi-arrow-left me-1"></i>Back to Order
                                    </a>
                                </div>
                                <div class="btn-group">
                                    <button onclick="window.print()" class="btn btn-primary font-causten">
                                        <i class="bi bi-printer me-1"></i>Print Invoice
                                    </button>
                                    <button onclick="downloadPDF()" class="btn btn-success font-causten">
                                        <i class="bi bi-download me-1"></i>Download PDF
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Invoice Container -->
                        <div class="card border-0 shadow-sm invoice-container">
                            <!-- Invoice Header -->
                            <div class="invoice-header">
                                <div class="row align-items-center">
                                    <div class="col-md-6">
                                        <div class="d-flex align-items-center">
                                            <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                                                 alt="foodXchange" class="company-logo me-3">
                                            <div>
                                                <h2 class="mb-1 font-causten">foodXchange</h2>
                                                <p class="mb-0 font-roboto-serif">B2B Food Marketplace Platform</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6 text-md-end">
                                        <div class="invoice-number font-causten">INV-2024-{order_id:03d}</div>
                                        <p class="mb-1 font-roboto-serif">Invoice Date: {datetime.now().strftime('%B %d, %Y')}</p>
                                        <p class="mb-0 font-roboto-serif">Due Date: {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}</p>
                                    </div>
                                </div>
                            </div>

                            <!-- Invoice Details -->
                            <div class="invoice-details">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h5 class="font-causten mb-3">Bill To:</h5>
                                        <div class="font-roboto-serif">
                                            <div class="fw-bold">ABC Restaurant</div>
                                            <div>123 Main Street</div>
                                            <div>New York, NY 10001</div>
                                            <div>United States</div>
                                            <div class="mt-2">
                                                <strong>Contact:</strong> John Smith<br>
                                                <strong>Email:</strong> john@abcrestaurant.com<br>
                                                <strong>Phone:</strong> +1 (555) 987-6543
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h5 class="font-causten mb-3">Ship To:</h5>
                                        <div class="font-roboto-serif">
                                            <div class="fw-bold">ABC Restaurant Warehouse</div>
                                            <div>456 Warehouse Avenue</div>
                                            <div>Brooklyn, NY 11201</div>
                                            <div>United States</div>
                                            <div class="mt-2">
                                                <strong>Contact:</strong> Warehouse Manager<br>
                                                <strong>Phone:</strong> +1 (555) 123-4567
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Order Information -->
                            <div class="p-4">
                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <h5 class="font-causten mb-2">Order Information</h5>
                                        <div class="font-roboto-serif">
                                            <div><strong>Order Number:</strong> ORD-2024-{order_id:03d}</div>
                                            <div><strong>Order Date:</strong> January 15, 2024</div>
                                            <div><strong>Delivery Date:</strong> January 20, 2024</div>
                                            <div><strong>Payment Terms:</strong> Net 30</div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h5 class="font-causten mb-2">Supplier Information</h5>
                                        <div class="font-roboto-serif">
                                            <div class="fw-bold">Mediterranean Delights</div>
                                            <div>789 Supplier Street</div>
                                            <div>Miami, FL 33101</div>
                                            <div>United States</div>
                                            <div class="mt-2">
                                                <strong>Contact:</strong> Maria Rodriguez<br>
                                                <strong>Email:</strong> maria@mediterraneandelights.com<br>
                                                <strong>Phone:</strong> +1 (555) 123-4567
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Items Table -->
                                <div class="table-responsive">
                                    <table class="table table-bordered">
                                        <thead class="table-light">
                                            <tr>
                                                <th class="font-causten">Item</th>
                                                <th class="font-causten">Description</th>
                                                <th class="font-causten text-end">Quantity</th>
                                                <th class="font-causten text-end">Unit Price</th>
                                                <th class="font-causten text-end">Total</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td class="font-roboto-serif">Organic Rice</td>
                                                <td class="font-roboto-serif">Premium organic basmati rice, Grade A quality</td>
                                                <td class="font-roboto-serif text-end">1,000 kg</td>
                                                <td class="font-roboto-serif text-end">$2.50</td>
                                                <td class="font-roboto-serif text-end fw-bold">$2,500.00</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>

                                <!-- Totals -->
                                <div class="row justify-content-end">
                                    <div class="col-md-4">
                                        <div class="total-section">
                                            <div class="row">
                                                <div class="col-6 font-roboto-serif">Subtotal:</div>
                                                <div class="col-6 text-end font-roboto-serif">$2,500.00</div>
                                            </div>
                                            <div class="row">
                                                <div class="col-6 font-roboto-serif">Shipping:</div>
                                                <div class="col-6 text-end font-roboto-serif">$150.00</div>
                                            </div>
                                            <div class="row">
                                                <div class="col-6 font-roboto-serif">Tax (8.875%):</div>
                                                <div class="col-6 text-end font-roboto-serif">$235.16</div>
                                            </div>
                                            <hr>
                                            <div class="row">
                                                <div class="col-6 font-causten fw-bold">Total:</div>
                                                <div class="col-6 text-end font-causten fw-bold">$2,885.16</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Terms and Conditions -->
                                <div class="mt-4">
                                    <h6 class="font-causten">Terms and Conditions:</h6>
                                    <div class="font-roboto-serif small">
                                        <ul class="mb-0">
                                            <li>Payment is due within 30 days of invoice date</li>
                                            <li>Late payments may incur additional charges</li>
                                            <li>All prices are subject to change without notice</li>
                                            <li>Returns must be made within 7 days of delivery</li>
                                            <li>Quality guarantee applies to all products</li>
                                        </ul>
                                    </div>
                                </div>

                                <!-- Signature Section -->
                                <div class="row mt-5">
                                    <div class="col-md-6">
                                        <div class="signature-line">
                                            <div class="font-causten fw-bold">Authorized Signature:</div>
                                            <div class="mt-3" style="border-bottom: 1px solid #000; width: 200px; height: 40px;"></div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="signature-line">
                                            <div class="font-causten fw-bold">Date:</div>
                                            <div class="mt-3" style="border-bottom: 1px solid #000; width: 200px; height: 40px;"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                function downloadPDF() {{
                    // This would typically call a backend endpoint to generate PDF
                    alert('PDF download feature would be implemented here. For now, please use the Print button and save as PDF.');
                }}
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Order invoice page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Invoice Error</title></head>
            <body>
                <h1>Invoice Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/orders/{order_id}">Back to Order</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/products/add", response_class=HTMLResponse, name="add_product")
async def add_product(request: Request):
    """Add new product page - Bootstrap styled"""
    try:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Add Product - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Add New Product</h1>
                                <p class="text-muted mb-0 font-roboto-serif">Add a new product to your catalog</p>
                            </div>
                            <div class="btn-group">
                                <a href="/products" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Products
                                </a>
                            </div>
                        </div>

                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-plus-circle me-2"></i>Product Information
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <form onsubmit="submitProduct(event)">
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="productName" class="form-label font-causten">Product Name *</label>
                                                    <input type="text" class="form-control font-roboto-serif" id="productName" required>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="productCategory" class="form-label font-causten">Category *</label>
                                                    <select class="form-select font-roboto-serif" id="productCategory" required>
                                                        <option value="">Select Category</option>
                                                        <option value="Grains">Grains</option>
                                                        <option value="Vegetables">Vegetables</option>
                                                        <option value="Fruits">Fruits</option>
                                                        <option value="Meat">Meat</option>
                                                        <option value="Dairy">Dairy</option>
                                                        <option value="Oils">Oils</option>
                                                        <option value="Spices">Spices</option>
                                                        <option value="Beverages">Beverages</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="productSupplier" class="form-label font-causten">Supplier *</label>
                                                    <select class="form-select font-roboto-serif" id="productSupplier" required>
                                                        <option value="">Select Supplier</option>
                                                        <option value="ABC Foods">ABC Foods</option>
                                                        <option value="Fresh Market">Fresh Market</option>
                                                        <option value="Quality Meats">Quality Meats</option>
                                                        <option value="Mediterranean Delights">Mediterranean Delights</option>
                                                        <option value="Organic Co">Organic Co</option>
                                                    </select>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="productUnit" class="form-label font-causten">Unit *</label>
                                                    <select class="form-select font-roboto-serif" id="productUnit" required>
                                                        <option value="">Select Unit</option>
                                                        <option value="kg">Kilogram (kg)</option>
                                                        <option value="g">Gram (g)</option>
                                                        <option value="L">Liter (L)</option>
                                                        <option value="ml">Milliliter (ml)</option>
                                                        <option value="pcs">Pieces (pcs)</option>
                                                        <option value="boxes">Boxes</option>
                                                        <option value="bottles">Bottles</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label for="productPrice" class="form-label font-causten">Price per Unit *</label>
                                                    <div class="input-group">
                                                        <span class="input-group-text">$</span>
                                                        <input type="number" class="form-control font-roboto-serif" id="productPrice" step="0.01" min="0" required>
                                                    </div>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label for="productStock" class="form-label font-causten">Initial Stock *</label>
                                                    <input type="number" class="form-control font-roboto-serif" id="productStock" min="0" required>
                                                </div>
                                            </div>
                                            
                                            <div class="mb-3">
                                                <label for="productDescription" class="form-label font-causten">Description</label>
                                                <textarea class="form-control font-roboto-serif" id="productDescription" rows="3" placeholder="Enter product description..."></textarea>
                                            </div>
                                            
                                            <div class="mb-3">
                                                <label for="productImage" class="form-label font-causten">Product Image</label>
                                                <input type="file" class="form-control font-roboto-serif" id="productImage" accept="image/*">
                                            </div>
                                            
                                            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                                <button type="button" class="btn btn-outline-secondary font-causten" onclick="window.location.href='/products'">
                                                    Cancel
                                                </button>
                                                <button type="submit" class="btn btn-primary font-causten">
                                                    <i class="bi bi-plus-circle me-2"></i>Add Product
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                function submitProduct(event) {
                    event.preventDefault();
                    
                    const formData = {
                        name: document.getElementById('productName').value,
                        category: document.getElementById('productCategory').value,
                        supplier: document.getElementById('productSupplier').value,
                        unit: document.getElementById('productUnit').value,
                        price: parseFloat(document.getElementById('productPrice').value),
                        stock: parseInt(document.getElementById('productStock').value),
                        description: document.getElementById('productDescription').value
                    };
                    
                    // Simulate form submission
                    alert('Product added successfully!');
                    console.log('Product data:', formData);
                    
                    // Redirect to products list
                    setTimeout(() => {
                        window.location.href = '/products';
                    }, 1000);
                }
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Add product page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Add Product Error</title></head>
            <body>
                <h1>Add Product Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/products">Back to Products</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/products/{product_id}", response_class=HTMLResponse, name="view_product")
async def view_product(request: Request, product_id: int):
    """View product details page - Bootstrap styled"""
    try:
        # Sample product data
        product = {
            "id": product_id,
            "name": "Organic Rice",
            "category": "Grains",
            "supplier": "ABC Foods",
            "unit": "kg",
            "price": 2.50,
            "stock": 1000,
            "description": "Premium organic basmati rice, Grade A quality. Sourced from certified organic farms.",
            "image": "/static/brand/logos/Favicon.png",
            "created_at": "2024-01-15",
            "last_updated": "2024-01-20"
        }
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Product Details - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Product Details</h1>
                                <p class="text-muted mb-0 font-roboto-serif">#{product_id} - {product['name']}</p>
                            </div>
                            <div class="btn-group">
                                <a href="/products" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Products
                                </a>
                                <button type="button" class="btn btn-primary font-causten" onclick="editProduct({product_id})">
                                    <i class="bi bi-pencil me-2"></i>Edit Product
                                </button>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-lg-8">
                                <!-- Product Information Card -->
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-box me-2"></i>Product Information
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Product Name</label>
                                                <div class="font-causten fw-bold">{product['name']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Category</label>
                                                <div>
                                                    <span class="badge bg-light text-dark font-causten">{product['category']}</span>
                                                </div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Supplier</label>
                                                <div class="font-causten fw-bold">{product['supplier']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Unit</label>
                                                <div class="font-causten">{product['unit']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Price per Unit</label>
                                                <div class="font-causten fw-bold text-success">${product['price']:.2f}/{product['unit']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Current Stock</label>
                                                <div class="font-causten">{product['stock']:,} {product['unit']}</div>
                                            </div>
                                            <div class="col-12 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Description</label>
                                                <div class="font-roboto-serif">{product['description']}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Product History Card -->
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-clock-history me-2"></i>Product History
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Created Date</label>
                                                <div class="font-causten">{product['created_at']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Last Updated</label>
                                                <div class="font-causten">{product['last_updated']}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-lg-4">
                                <!-- Product Image Card -->
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-image me-2"></i>Product Image
                                        </h5>
                                    </div>
                                    <div class="card-body text-center">
                                        <img src="{product['image']}" alt="{product['name']}" class="img-fluid rounded" style="max-height: 200px;">
                                    </div>
                                </div>

                                <!-- Quick Actions Card -->
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-lightning me-2"></i>Quick Actions
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-grid gap-2">
                                            <button type="button" class="btn btn-outline-primary font-causten" onclick="editProduct({product_id})">
                                                <i class="bi bi-pencil me-2"></i>Edit Product
                                            </button>
                                            <button type="button" class="btn btn-outline-success font-causten" onclick="createRFQ({product_id})">
                                                <i class="bi bi-file-earmark-plus me-2"></i>Create RFQ
                                            </button>
                                            <button type="button" class="btn btn-outline-info font-causten" onclick="viewHistory({product_id})">
                                                <i class="bi bi-clock-history me-2"></i>View History
                                            </button>
                                            <button type="button" class="btn btn-outline-danger font-causten" onclick="deleteProduct({product_id})">
                                                <i class="bi bi-trash me-2"></i>Delete Product
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                function editProduct(productId) {
                    alert(`Editing product ${productId}...`);
                }
                
                function createRFQ(productId) {
                    alert(`Creating RFQ for product ${productId}...`);
                }
                
                function viewHistory(productId) {
                    alert(`Viewing history for product ${productId}...`);
                }
                
                function deleteProduct(productId) {
                    if (confirm(`Are you sure you want to delete product ${productId}?`)) {
                        alert(`Product ${productId} deleted successfully!`);
                        window.location.href = '/products';
                    }
                }
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"View product page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Product Details Error</title></head>
            <body>
                <h1>Product Details Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/products">Back to Products</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/orders/{order_id}", response_class=HTMLResponse, name="view_order")
async def view_order(request: Request, order_id: int):
    """View order details page - Bootstrap styled"""
    try:
        # Sample order data
        order = {
            "id": order_id,
            "order_number": f"ORD-2024-{order_id:03d}",
            "order_date": "2024-01-15",
            "status": "Delivered",
            "total_amount": 2500.00,
            "product_name": "Organic Rice",
            "category": "Grains",
            "quantity": 1000,
            "unit": "kg",
            "unit_price": 2.50,
            "supplier_name": "Mediterranean Delights",
            "contact_person": "Maria Rodriguez",
            "email": "maria@mediterraneandelights.com",
            "phone": "+1 (555) 123-4567",
            "delivery_date": "2024-01-20",
            "notes": "Premium quality organic rice for restaurant use"
        }
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Order Details - foodXchange</title>
            <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div>
                                <h1 class="h3 mb-1 font-causten">Order Details</h1>
                                <p class="text-muted mb-0 font-roboto-serif">{order['order_number']} - {order['product_name']}</p>
                            </div>
                            <div class="btn-group">
                                <a href="/orders" class="btn btn-outline-secondary font-causten">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Orders
                                </a>
                                <a href="/orders/{order_id}/edit" class="btn btn-primary font-causten">
                                    <i class="bi bi-pencil me-2"></i>Edit Order
                                </a>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-lg-8">
                                <!-- Order Information Card -->
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-file-text me-2"></i>Order Information
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Order Number</label>
                                                <div class="font-causten fw-bold">{order['order_number']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Order Date</label>
                                                <div class="font-causten">{order['order_date']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Status</label>
                                                <div>
                                                    <span class="badge bg-success font-causten">{order['status']}</span>
                                                </div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Total Amount</label>
                                                <div class="font-causten fw-bold text-success">${order['total_amount']:,.2f}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Product Details Card -->
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-box me-2"></i>Product Details
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Product Name</label>
                                                <div class="font-causten fw-bold">{order['product_name']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Category</label>
                                                <div class="font-causten">{order['category']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Quantity</label>
                                                <div class="font-causten">{order['quantity']:,} {order['unit']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Unit Price</label>
                                                <div class="font-causten">${order['unit_price']:.2f}/{order['unit']}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Supplier Information Card -->
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-building me-2"></i>Supplier Information
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Supplier Name</label>
                                                <div class="font-causten fw-bold">{order['supplier_name']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Contact Person</label>
                                                <div class="font-causten">{order['contact_person']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Email</label>
                                                <div class="font-causten">{order['email']}</div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label text-muted font-roboto-serif">Phone</label>
                                                <div class="font-causten">{order['phone']}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-lg-4">
                                <!-- Order Timeline Card -->
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-clock-history me-2"></i>Order Timeline
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="timeline">
                                            <div class="timeline-item">
                                                <div class="timeline-marker bg-success"></div>
                                                <div class="timeline-content">
                                                    <h6 class="font-causten">Order Delivered</h6>
                                                    <small class="text-muted font-roboto-serif">{order['delivery_date']} 02:15 PM</small>
                                                    <p class="mb-0 font-roboto-serif">Order has been successfully delivered to warehouse</p>
                                                </div>
                                            </div>
                                            <div class="timeline-item">
                                                <div class="timeline-marker bg-info"></div>
                                                <div class="timeline-content">
                                                    <h6 class="font-causten">In Transit</h6>
                                                    <small class="text-muted font-roboto-serif">2024-01-18 09:30 AM</small>
                                                    <p class="mb-0 font-roboto-serif">Order shipped from supplier facility</p>
                                                </div>
                                            </div>
                                            <div class="timeline-item">
                                                <div class="timeline-marker bg-warning"></div>
                                                <div class="timeline-content">
                                                    <h6 class="font-causten">Order Confirmed</h6>
                                                    <small class="text-muted font-roboto-serif">2024-01-15 10:30 AM</small>
                                                    <p class="mb-0 font-roboto-serif">Order confirmed by supplier</p>
                                                </div>
                                            </div>
                                            <div class="timeline-item">
                                                <div class="timeline-marker bg-primary"></div>
                                                <div class="timeline-content">
                                                    <h6 class="font-causten">Order Placed</h6>
                                                    <small class="text-muted font-roboto-serif">2024-01-15 10:00 AM</small>
                                                    <p class="mb-0 font-roboto-serif">Order created in system</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Quick Actions Card -->
                                <div class="card border-0 shadow-sm">
                                    <div class="card-header bg-white">
                                        <h5 class="card-title mb-0 font-causten">
                                            <i class="bi bi-lightning me-2"></i>Quick Actions
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-grid gap-2">
                                            <a href="/orders/{order_id}/edit" class="btn btn-outline-primary font-causten">
                                                <i class="bi bi-pencil me-2"></i>Edit Order
                                            </a>
                                            <a href="/orders/{order_id}/invoice" class="btn btn-outline-success font-causten">
                                                <i class="bi bi-printer me-2"></i>Print Invoice
                                            </a>
                                            <button type="button" class="btn btn-outline-info font-causten" onclick="contactSupplier()">
                                                <i class="bi bi-envelope me-2"></i>Contact Supplier
                                            </button>
                                            <button type="button" class="btn btn-outline-warning font-causten" onclick="reorder()">
                                                <i class="bi bi-arrow-repeat me-2"></i>Reorder
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style>
            .timeline {
                position: relative;
                padding-left: 30px;
            }
            .timeline-item {
                position: relative;
                margin-bottom: 25px;
            }
            .timeline-marker {
                position: absolute;
                left: -35px;
                top: 5px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 0 0 2px #dee2e6;
            }
            .timeline-content {
                padding-left: 10px;
            }
            .timeline-content h6 {
                margin-bottom: 5px;
            }
            .timeline-content p {
                font-size: 0.875rem;
            }
            </style>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                function contactSupplier() {
                    alert('Contacting supplier...');
                }
                
                function reorder() {
                    if (confirm('Are you sure you want to reorder this item?')) {
                        alert('Creating new order...');
                    }
                }
            </script>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"View order page error: {e}")
        return HTMLResponse(content=f"""
        <html>
            <head><title>Order Details Error</title></head>
            <body>
                <h1>Order Details Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/orders">Back to Orders</a>
            </body>
        </html>
        """, status_code=500)

# Favicon route for better browser compatibility
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon for browser compatibility"""
    return RedirectResponse(url="/static/brand/logos/Favicon.png")

@app.get("/favicon.png")
async def favicon_png():
    """Serve favicon PNG for direct access"""
    return RedirectResponse(url="/static/brand/logos/Favicon.png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 