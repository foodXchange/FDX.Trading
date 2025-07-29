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
app.mount("/static", StaticFiles(directory="static"), name="static")

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