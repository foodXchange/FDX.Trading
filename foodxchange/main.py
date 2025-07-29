"""
FoodXchange - AI-Powered B2B Food Sourcing Platform
Main FastAPI application with integrated product analysis system
"""

from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FoodXchange",
    description="AI-Powered B2B Food Sourcing Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="foodxchange/static"), name="static")

# Simple database session mock (replace with actual database)
def get_db():
    return None

def get_current_user_context(request: Request, db=None):
    return None

# Import and include all route modules
try:
    from .routes import (
        auth_routes,
        supplier_routes,
        product_routes,
        rfq_routes,
        quote_routes,
        order_routes,
        notification_routes,
        file_routes,
        product_analysis_routes
    )
    
    # Include all routers
    app.include_router(auth_routes.router)
    app.include_router(supplier_routes.router)
    app.include_router(product_routes.router)
    app.include_router(rfq_routes.router)
    app.include_router(quote_routes.router)
    app.include_router(order_routes.router)
    app.include_router(notification_routes.router)
    app.include_router(file_routes.router)
    app.include_router(product_analysis_routes.router)
    
    logger.info("✅ All route modules loaded successfully")
    
except ImportError as e:
    logger.warning(f"⚠️ Some route modules could not be loaded: {e}")

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    """Landing page - Bootstrap styled"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FoodXchange - AI-Powered B2B Food Sourcing</title>
        <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        <style>
            .hero-section {
                background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
                color: white;
                padding: 100px 0;
            }
            .hero-title {
                font-size: 3.5rem;
                font-weight: bold;
                margin-bottom: 1rem;
            }
            .hero-subtitle {
                font-size: 1.25rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            .feature-card {
                border: none;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
                height: 100%;
            }
            .feature-card:hover {
                transform: translateY(-5px);
            }
            .feature-icon {
                font-size: 3rem;
                color: #FF6B35;
                margin-bottom: 1rem;
            }
            .ai-feature {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                         alt="FoodXchange" height="40">
                    <span class="ms-2 font-causten fw-bold text-primary">FoodXchange</span>
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link font-causten" href="/product-analysis">AI Analysis</a>
                    <a class="nav-link font-causten" href="/suppliers">Suppliers</a>
                    <a class="nav-link font-causten" href="/login">Login</a>
                    <a class="nav-link font-causten" href="/register">Register</a>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <section class="hero-section">
            <div class="container text-center">
                <h1 class="hero-title font-causten">AI-Powered Food Sourcing</h1>
                <p class="hero-subtitle font-roboto-serif">
                    Upload product images, get instant AI analysis, and find the best suppliers worldwide.
                    Streamline your B2B food sourcing with intelligent automation.
                </p>
                <div class="d-flex justify-content-center gap-3">
                    <a href="/product-analysis" class="btn btn-light btn-lg font-causten">
                        <i class="bi bi-robot me-2"></i>Try AI Analysis
                    </a>
                    <a href="/register" class="btn btn-outline-light btn-lg font-causten">
                        <i class="bi bi-person-plus me-2"></i>Get Started
                    </a>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="py-5">
            <div class="container">
                <div class="row text-center mb-5">
                    <div class="col-12">
                        <h2 class="font-causten fw-bold mb-3">Powerful Features</h2>
                        <p class="font-roboto-serif text-muted">Everything you need for efficient food sourcing</p>
                    </div>
                </div>
                
                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="card feature-card ai-feature">
                            <div class="card-body text-center p-4">
                                <i class="bi bi-robot feature-icon"></i>
                                <h4 class="font-causten mb-3">AI Product Analysis</h4>
                                <p class="font-roboto-serif">
                                    Upload product images and get instant AI-powered analysis, 
                                    specifications, and sourcing recommendations.
                                </p>
                                <a href="/product-analysis" class="btn btn-light font-causten">Try Now</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card feature-card">
                            <div class="card-body text-center p-4">
                                <i class="bi bi-shop feature-icon"></i>
                                <h4 class="font-causten mb-3">Supplier Network</h4>
                                <p class="font-roboto-serif">
                                    Connect with verified suppliers worldwide. 
                                    Browse products, compare prices, and manage relationships.
                                </p>
                                <a href="/suppliers" class="btn btn-primary font-causten">Browse Suppliers</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card feature-card">
                            <div class="card-body text-center p-4">
                                <i class="bi bi-file-earmark-text feature-icon"></i>
                                <h4 class="font-causten mb-3">Smart RFQs</h4>
                                <p class="font-roboto-serif">
                                    Create intelligent Requests for Quotes with AI assistance. 
                                    Get better responses and faster sourcing.
                                </p>
                                <a href="/rfqs" class="btn btn-primary font-causten">Create RFQ</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- How It Works Section -->
        <section class="py-5 bg-light">
            <div class="container">
                <div class="row text-center mb-5">
                    <div class="col-12">
                        <h2 class="font-causten fw-bold mb-3">How It Works</h2>
                        <p class="font-roboto-serif text-muted">Simple 3-step process to find your perfect suppliers</p>
                    </div>
                </div>
                
                <div class="row g-4">
                    <div class="col-md-4 text-center">
                        <div class="bg-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                             style="width: 80px; height: 80px;">
                            <i class="bi bi-camera fs-1 text-primary"></i>
                        </div>
                        <h5 class="font-causten">1. Upload Image</h5>
                        <p class="font-roboto-serif text-muted">
                            Upload a product image or search by name
                        </p>
                    </div>
                    
                    <div class="col-md-4 text-center">
                        <div class="bg-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                             style="width: 80px; height: 80px;">
                            <i class="bi bi-robot fs-1 text-primary"></i>
                        </div>
                        <h5 class="font-causten">2. AI Analysis</h5>
                        <p class="font-roboto-serif text-muted">
                            Get instant product analysis and specifications
                        </p>
                    </div>
                    
                    <div class="col-md-4 text-center">
                        <div class="bg-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                             style="width: 80px; height: 80px;">
                            <i class="bi bi-check-circle fs-1 text-primary"></i>
                        </div>
                        <h5 class="font-causten">3. Find Suppliers</h5>
                        <p class="font-roboto-serif text-muted">
                            Connect with verified suppliers and get quotes
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="bg-dark text-white py-4">
            <div class="container">
                <div class="row">
                    <div class="col-md-6">
                        <h5 class="font-causten">FoodXchange</h5>
                        <p class="font-roboto-serif text-muted">
                            AI-powered B2B food sourcing platform
                        </p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <p class="font-roboto-serif text-muted mb-0">
                            © 2024 FoodXchange. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page with AI analysis integration"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - FoodXchange</title>
        <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        <style>
            .dashboard-card {
                border: none;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }
            .dashboard-card:hover {
                transform: translateY(-2px);
            }
            .ai-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                         alt="FoodXchange" height="40">
                    <span class="ms-2 font-causten fw-bold text-primary">FoodXchange</span>
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link font-causten active" href="/dashboard">Dashboard</a>
                    <a class="nav-link font-causten" href="/product-analysis">AI Analysis</a>
                    <a class="nav-link font-causten" href="/suppliers">Suppliers</a>
                    <a class="nav-link font-causten" href="/logout">Logout</a>
                </div>
            </div>
        </nav>

        <!-- Dashboard Content -->
        <div class="container mt-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h1 class="font-causten fw-bold">Dashboard</h1>
                    <p class="font-roboto-serif text-muted">Welcome to your AI-powered sourcing dashboard</p>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="row g-4 mb-4">
                <div class="col-md-6">
                    <div class="card dashboard-card ai-card">
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-robot fs-1 me-3"></i>
                                <div>
                                    <h4 class="font-causten mb-1">AI Product Analysis</h4>
                                    <p class="font-roboto-serif mb-0">Analyze products with AI</p>
                                </div>
                            </div>
                            <a href="/product-analysis" class="btn btn-light font-causten">
                                <i class="bi bi-camera me-2"></i>Upload Image
                            </a>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card dashboard-card">
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-shop fs-1 me-3 text-primary"></i>
                                <div>
                                    <h4 class="font-causten mb-1">Find Suppliers</h4>
                                    <p class="font-roboto-serif mb-0">Browse supplier network</p>
                                </div>
                            </div>
                            <a href="/suppliers" class="btn btn-primary font-causten">
                                <i class="bi bi-search me-2"></i>Browse Suppliers
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Cards -->
            <div class="row g-4">
                <div class="col-md-3">
                    <div class="card dashboard-card">
                        <div class="card-body text-center">
                            <i class="bi bi-robot text-primary fs-1 mb-2"></i>
                            <h3 class="font-causten">12</h3>
                            <p class="font-roboto-serif text-muted">AI Analyses</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card dashboard-card">
                        <div class="card-body text-center">
                            <i class="bi bi-shop text-success fs-1 mb-2"></i>
                            <h3 class="font-causten">45</h3>
                            <p class="font-roboto-serif text-muted">Suppliers</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card dashboard-card">
                        <div class="card-body text-center">
                            <i class="bi bi-file-text text-warning fs-1 mb-2"></i>
                            <h3 class="font-causten">8</h3>
                            <p class="font-roboto-serif text-muted">Active RFQs</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card dashboard-card">
                        <div class="card-body text-center">
                            <i class="bi bi-check-circle text-info fs-1 mb-2"></i>
                            <h3 class="font-causten">23</h3>
                            <p class="font-roboto-serif text-muted">Completed Orders</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Register - FoodXchange</title>
        <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Roboto Serif', serif;
            }
            .register-container {
                max-width: 500px;
                width: 100%;
                padding: 20px;
            }
            .register-card {
                background: white;
                border: none;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                padding: 3rem;
                position: relative;
                overflow: hidden;
            }
            .register-card::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255, 127, 0, 0.05) 0%, transparent 70%);
                transform: rotate(45deg);
            }
            .logo-section {
                text-align: center;
                margin-bottom: 2rem;
                z-index: 1;
                position: relative;
            }
            .logo-section img {
                max-width: 180px;
                margin-bottom: 1rem;
            }
            .form-control {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 0.875rem 1.25rem;
                font-size: 1rem;
                transition: all 0.3s ease;
                background-color: #f8f9fa;
            }
            .form-control:focus {
                border-color: #ff7f00;
                box-shadow: 0 0 0 0.2rem rgba(255, 127, 0, 0.1);
                background-color: white;
            }
            .form-label {
                font-weight: 600;
                color: #333;
                margin-bottom: 0.5rem;
                font-family: 'Causten', sans-serif;
            }
            .btn-register {
                background: linear-gradient(135deg, #ff7f00 0%, #ff9a33 100%);
                border: none;
                border-radius: 12px;
                padding: 0.875rem;
                font-size: 1.1rem;
                font-weight: 600;
                color: white;
                transition: all 0.3s ease;
                font-family: 'Causten', sans-serif;
            }
            .btn-register:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(255, 127, 0, 0.3);
                background: linear-gradient(135deg, #ff9a33 0%, #ff7f00 100%);
            }
            .divider {
                text-align: center;
                margin: 2rem 0;
                position: relative;
            }
            .divider::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 0;
                right: 0;
                height: 1px;
                background: #e0e0e0;
            }
            .divider span {
                background: white;
                padding: 0 1rem;
                position: relative;
                color: #666;
                font-size: 0.9rem;
            }
            .login-link {
                text-align: center;
                margin-top: 2rem;
                color: #666;
            }
            .login-link a {
                color: #ff7f00;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.3s ease;
            }
            .login-link a:hover {
                color: #ff9a33;
                text-decoration: underline;
            }
            .feature-item {
                display: flex;
                align-items: center;
                margin-bottom: 1rem;
                color: #666;
                font-size: 0.9rem;
            }
            .feature-item i {
                color: #ff7f00;
                margin-right: 0.5rem;
            }
            .alert {
                border-radius: 12px;
                border: none;
                padding: 1rem 1.25rem;
            }
            .alert-danger {
                background-color: #fee;
                color: #c33;
            }
        </style>
    </head>
    <body>
        <div class="register-container">
            <div class="register-card">
                <div class="logo-section">
                    <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                         alt="FoodXchange Logo">
                    <h2 class="font-causten fw-bold mb-1">Create Your Account</h2>
                    <p class="text-muted">Join the AI-powered B2B food sourcing revolution</p>
                </div>
                
                <form method="POST" action="/auth/register" class="position-relative" style="z-index: 1;">
                    <div class="row">
                        <div class="col-12 mb-3">
                            <label for="name" class="form-label">Full Name</label>
                            <div class="input-group">
                                <span class="input-group-text bg-transparent border-end-0" style="border-radius: 12px 0 0 12px;">
                                    <i class="bi bi-person text-muted"></i>
                                </span>
                                <input type="text" class="form-control border-start-0" id="name" name="name" 
                                       placeholder="John Doe" required style="border-radius: 0 12px 12px 0;">
                            </div>
                        </div>
                        
                        <div class="col-12 mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <div class="input-group">
                                <span class="input-group-text bg-transparent border-end-0" style="border-radius: 12px 0 0 12px;">
                                    <i class="bi bi-envelope text-muted"></i>
                                </span>
                                <input type="email" class="form-control border-start-0" id="email" name="email" 
                                       placeholder="john@company.com" required style="border-radius: 0 12px 12px 0;">
                            </div>
                        </div>
                        
                        <div class="col-12 mb-3">
                            <label for="password" class="form-label">Password</label>
                            <div class="input-group">
                                <span class="input-group-text bg-transparent border-end-0" style="border-radius: 12px 0 0 12px;">
                                    <i class="bi bi-lock text-muted"></i>
                                </span>
                                <input type="password" class="form-control border-start-0" id="password" name="password" 
                                       placeholder="Minimum 6 characters" required minlength="6" style="border-radius: 0 12px 12px 0;">
                            </div>
                        </div>
                        
                        <div class="col-12 mb-4">
                            <label for="company" class="form-label">Company Name <span class="text-muted">(Optional)</span></label>
                            <div class="input-group">
                                <span class="input-group-text bg-transparent border-end-0" style="border-radius: 12px 0 0 12px;">
                                    <i class="bi bi-building text-muted"></i>
                                </span>
                                <input type="text" class="form-control border-start-0" id="company" name="company" 
                                       placeholder="Your Company Ltd." style="border-radius: 0 12px 12px 0;">
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-register w-100 mb-3">
                        <i class="bi bi-person-plus-fill me-2"></i>Create Account
                    </button>
                    
                    <div class="feature-item">
                        <i class="bi bi-check-circle-fill"></i>
                        <span>AI-powered product analysis and matching</span>
                    </div>
                    <div class="feature-item">
                        <i class="bi bi-check-circle-fill"></i>
                        <span>Access to verified B2B suppliers</span>
                    </div>
                    <div class="feature-item">
                        <i class="bi bi-check-circle-fill"></i>
                        <span>Automated RFQ and quote management</span>
                    </div>
                </form>
                
                <div class="divider">
                    <span>Already have an account?</span>
                </div>
                
                <div class="login-link">
                    <a href="/login" class="font-causten">Sign in to your account</a>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Show error message if present in URL
            const urlParams = new URLSearchParams(window.location.search);
            const error = urlParams.get('error');
            if (error) {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger alert-dismissible fade show mb-3';
                alertDiv.innerHTML = `
                    <i class="bi bi-exclamation-circle-fill me-2"></i>${error}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                document.querySelector('form').insertAdjacentElement('beforebegin', alertDiv);
            }
        </script>
    </body>
    </html>
    """)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - FoodXchange</title>
        <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Roboto Serif', serif;
            }
            .login-container {
                max-width: 450px;
                width: 100%;
                padding: 20px;
            }
            .login-card {
                background: white;
                border: none;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                padding: 3rem;
                position: relative;
                overflow: hidden;
            }
            .login-card::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255, 127, 0, 0.05) 0%, transparent 70%);
                transform: rotate(45deg);
            }
            .logo-section {
                text-align: center;
                margin-bottom: 2rem;
                z-index: 1;
                position: relative;
            }
            .logo-section img {
                max-width: 180px;
                margin-bottom: 1rem;
            }
            .form-control {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 0.875rem 1.25rem;
                font-size: 1rem;
                transition: all 0.3s ease;
                background-color: #f8f9fa;
            }
            .form-control:focus {
                border-color: #ff7f00;
                box-shadow: 0 0 0 0.2rem rgba(255, 127, 0, 0.1);
                background-color: white;
            }
            .form-label {
                font-weight: 600;
                color: #333;
                margin-bottom: 0.5rem;
                font-family: 'Causten', sans-serif;
            }
            .btn-login {
                background: linear-gradient(135deg, #ff7f00 0%, #ff9a33 100%);
                border: none;
                border-radius: 12px;
                padding: 0.875rem;
                font-size: 1.1rem;
                font-weight: 600;
                color: white;
                transition: all 0.3s ease;
                font-family: 'Causten', sans-serif;
            }
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(255, 127, 0, 0.3);
                background: linear-gradient(135deg, #ff9a33 0%, #ff7f00 100%);
            }
            .divider {
                text-align: center;
                margin: 2rem 0;
                position: relative;
            }
            .divider::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 0;
                right: 0;
                height: 1px;
                background: #e0e0e0;
            }
            .divider span {
                background: white;
                padding: 0 1rem;
                position: relative;
                color: #666;
                font-size: 0.9rem;
            }
            .register-link {
                text-align: center;
                margin-top: 2rem;
                color: #666;
            }
            .register-link a {
                color: #ff7f00;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.3s ease;
            }
            .register-link a:hover {
                color: #ff9a33;
                text-decoration: underline;
            }
            .alert {
                border-radius: 12px;
                border: none;
                padding: 1rem 1.25rem;
            }
            .alert-danger {
                background-color: #fee;
                color: #c33;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-card">
                <div class="logo-section">
                    <img src="/static/brand/logos/Food Xchange - Logo_Orange-on-White Version-04.png" 
                         alt="FoodXchange Logo">
                    <h2 class="font-causten fw-bold mb-1">Welcome Back</h2>
                    <p class="text-muted">Sign in to your FoodXchange account</p>
                </div>
                
                <form method="POST" action="/auth/login" class="position-relative" style="z-index: 1;">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email Address</label>
                        <div class="input-group">
                            <span class="input-group-text bg-transparent border-end-0" style="border-radius: 12px 0 0 12px;">
                                <i class="bi bi-envelope text-muted"></i>
                            </span>
                            <input type="email" class="form-control border-start-0" id="email" name="email" 
                                   placeholder="your@email.com" required style="border-radius: 0 12px 12px 0;">
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <label for="password" class="form-label">Password</label>
                        <div class="input-group">
                            <span class="input-group-text bg-transparent border-end-0" style="border-radius: 12px 0 0 12px;">
                                <i class="bi bi-lock text-muted"></i>
                            </span>
                            <input type="password" class="form-control border-start-0" id="password" name="password" 
                                   placeholder="Your password" required style="border-radius: 0 12px 12px 0;">
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-login w-100 mb-3">
                        <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
                    </button>
                </form>
                
                <div class="divider">
                    <span>New to FoodXchange?</span>
                </div>
                
                <div class="register-link">
                    <a href="/register" class="font-causten">Create your free account</a>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Show error message if present in URL
            const urlParams = new URLSearchParams(window.location.search);
            const error = urlParams.get('error');
            if (error) {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger alert-dismissible fade show mb-3';
                alertDiv.innerHTML = `
                    <i class="bi bi-exclamation-circle-fill me-2"></i>${error}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                document.querySelector('form').insertAdjacentElement('beforebegin', alertDiv);
            }
        </script>
    </body>
    </html>
    """)

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    return RedirectResponse(url="/static/brand/logos/Favicon.png")

@app.get("/favicon.png")
async def favicon_png():
    """Serve favicon PNG"""
    return RedirectResponse(url="/static/brand/logos/Favicon.png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 