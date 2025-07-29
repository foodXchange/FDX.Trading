"""
Product Analysis Routes for FoodXchange
AI-powered product analysis and brief generation endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any
import json
import logging
from datetime import datetime

# Local imports
from ..services.product_analysis_service import product_analysis_service
from ..database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/product-analysis", tags=["Product Analysis"])

@router.get("/", response_class=HTMLResponse)
async def product_analysis_page():
    """Product Analysis Dashboard - Bootstrap styled"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Product Analysis - FoodXchange</title>
        <link rel="icon" type="image/png" href="/static/brand/logos/Favicon.png">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <link rel="stylesheet" href="/static/brand/fx-fonts.css">
        <style>
            .upload-area {
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                border-color: #0d6efd;
                background-color: #f8f9fa;
            }
            .upload-area.dragover {
                border-color: #0d6efd;
                background-color: #e7f3ff;
            }
            .analysis-result {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
            }
            .brief-card {
                background: white;
                border-radius: 10px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 15px 0;
            }
            .demo-mode {
                background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
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
                    <a class="nav-link font-causten" href="/dashboard">Dashboard</a>
                    <a class="nav-link font-causten" href="/suppliers">Suppliers</a>
                    <a class="nav-link font-causten active" href="/product-analysis">AI Analysis</a>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <h1 class="font-causten fw-bold mb-4">
                        <i class="bi bi-robot me-2"></i>AI Product Analysis
                    </h1>
                    <p class="font-roboto-serif text-muted mb-4">
                        Upload a product image or search by name to get AI-powered analysis and sourcing recommendations.
                    </p>
                    
                    <!-- Demo Mode Notice -->
                    <div class="demo-mode">
                        <i class="bi bi-info-circle me-2"></i>
                        <strong>Demo Mode:</strong> This is a demonstration of the AI analysis system. 
                        Upload an image or search for a product to see how it works!
                    </div>
                </div>
            </div>

            <!-- Analysis Methods -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="font-causten mb-0">
                                <i class="bi bi-camera me-2"></i>Image Analysis
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="upload-area" id="uploadArea">
                                <i class="bi bi-cloud-upload display-4 text-muted mb-3"></i>
                                <h5 class="font-causten">Upload Product Image</h5>
                                <p class="font-roboto-serif text-muted">
                                    Drag and drop an image here or click to browse
                                </p>
                                <input type="file" id="imageInput" accept="image/*" class="d-none">
                                <button class="btn btn-primary font-causten" onclick="document.getElementById('imageInput').click()">
                                    Choose Image
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="font-causten mb-0">
                                <i class="bi bi-search me-2"></i>Text Search
                            </h5>
                        </div>
                        <div class="card-body">
                            <form id="searchForm">
                                <div class="mb-3">
                                    <label for="searchInput" class="form-label font-causten">Product Name or Description</label>
                                    <input type="text" class="form-control font-roboto-serif" id="searchInput" 
                                           placeholder="e.g., Organic dried cranberries, Fresh salmon fillets">
                                </div>
                                <button type="submit" class="btn btn-primary font-causten">
                                    <i class="bi bi-search me-2"></i>Analyze Product
                                </button>
                            </form>
                            
                            <!-- Quick Examples -->
                            <div class="mt-3">
                                <small class="text-muted font-roboto-serif">Try these examples:</small>
                                <div class="d-flex flex-wrap gap-1 mt-1">
                                    <button class="btn btn-sm btn-outline-secondary" onclick="setSearchText('Organic dried cranberries')">Cranberries</button>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="setSearchText('Fresh salmon fillets')">Salmon</button>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="setSearchText('Extra virgin olive oil')">Olive Oil</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Results Area -->
            <div id="resultsArea" class="d-none">
                <div class="analysis-result">
                    <h3 class="font-causten mb-3">
                        <i class="bi bi-lightbulb me-2"></i>AI Analysis Results
                    </h3>
                    <div id="analysisContent"></div>
                </div>

                <div class="brief-card">
                    <h4 class="font-causten mb-3">
                        <i class="bi bi-file-text me-2"></i>Product Brief
                    </h4>
                    <div id="briefContent"></div>
                </div>

                <div class="brief-card">
                    <h4 class="font-causten mb-3">
                        <i class="bi bi-shop me-2"></i>Sourcing Recommendations
                    </h4>
                    <div id="sourcingContent"></div>
                </div>
            </div>

            <!-- Loading Spinner -->
            <div id="loadingSpinner" class="text-center d-none">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="font-causten mt-2">AI is analyzing your product...</p>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // File upload handling
            const uploadArea = document.getElementById('uploadArea');
            const imageInput = document.getElementById('imageInput');
            const searchForm = document.getElementById('searchForm');
            const resultsArea = document.getElementById('resultsArea');
            const loadingSpinner = document.getElementById('loadingSpinner');

            // Drag and drop functionality
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleImageUpload(files[0]);
                }
            });

            imageInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleImageUpload(e.target.files[0]);
                }
            });

            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const searchText = document.getElementById('searchInput').value;
                if (searchText.trim()) {
                    handleTextSearch(searchText);
                }
            });

            function setSearchText(text) {
                document.getElementById('searchInput').value = text;
                handleTextSearch(text);
            }

            async function handleImageUpload(file) {
                showLoading();
                
                // For demo purposes, simulate AI analysis
                setTimeout(() => {
                    const mockResult = {
                        success: true,
                        analysis: {
                            product_name: "Product from Image",
                            category: "Food Product",
                            description: "AI analysis of uploaded product image",
                            tags: ["food", "product", "fresh"],
                            confidence_score: 0.85
                        },
                        brief: {
                            product_name: "Product from Image",
                            category: "Food Product",
                            description: "High-quality food product suitable for B2B sourcing",
                            specifications: {
                                "Quality": "Premium Grade",
                                "Certification": "ISO 22000",
                                "Shelf Life": "12 months"
                            },
                            packaging_options: ["100g", "250g", "500g", "1kg"],
                            target_market: "B2B Food Industry",
                            quality_standards: ["ISO 22000", "HACCP"],
                            estimated_price_range: {"min": 5.0, "max": 15.0, "currency": "USD"},
                            supplier_requirements: ["Food safety certification", "Quality assurance"],
                            market_insights: "Growing demand for quality food products"
                        },
                        similar_products: [
                            {
                                id: 1,
                                name: "Similar Product 1",
                                supplier: "Fresh Foods Co",
                                category: "Food Product",
                                price: 5.99,
                                rating: 4.5,
                                availability: "In Stock"
                            },
                            {
                                id: 2,
                                name: "Similar Product 2",
                                supplier: "Organic Farms Ltd",
                                category: "Food Product",
                                price: 7.50,
                                rating: 4.8,
                                availability: "In Stock"
                            }
                        ]
                    };
                    displayResults(mockResult);
                    hideLoading();
                }, 2000);
            }

            async function handleTextSearch(searchText) {
                showLoading();

                // For demo purposes, simulate AI analysis
                setTimeout(() => {
                    const mockResult = {
                        success: true,
                        analysis: {
                            product_name: searchText,
                            category: "Food Product",
                            description: `AI analysis of "${searchText}" - premium quality food product`,
                            tags: ["food", "organic", "premium"],
                            confidence_score: 0.90
                        },
                        brief: {
                            product_name: searchText,
                            category: "Food Product",
                            description: `Comprehensive analysis of ${searchText} for B2B sourcing`,
                            specifications: {
                                "Quality": "Premium Grade",
                                "Certification": "Organic Certified",
                                "Origin": "Global Sourcing",
                                "Processing": "Minimal Processing"
                            },
                            packaging_options: ["100g", "250g", "500g", "1kg", "5kg"],
                            target_market: "B2B Food Industry",
                            quality_standards: ["ISO 22000", "HACCP", "Organic"],
                            estimated_price_range: {"min": 8.0, "max": 25.0, "currency": "USD"},
                            supplier_requirements: ["Organic certification", "Food safety certification", "Quality assurance"],
                            market_insights: "High demand for organic and premium food products"
                        },
                        similar_products: [
                            {
                                id: 1,
                                name: `Premium ${searchText}`,
                                supplier: "Organic Farms Ltd",
                                category: "Food Product",
                                price: 12.99,
                                rating: 4.8,
                                availability: "In Stock"
                            },
                            {
                                id: 2,
                                name: `Organic ${searchText}`,
                                supplier: "Fresh Foods Co",
                                category: "Food Product",
                                price: 9.50,
                                rating: 4.5,
                                availability: "In Stock"
                            },
                            {
                                id: 3,
                                name: `Bulk ${searchText}`,
                                supplier: "Global Seafood",
                                category: "Food Product",
                                price: 6.75,
                                rating: 4.2,
                                availability: "In Stock"
                            }
                        ]
                    };
                    displayResults(mockResult);
                    hideLoading();
                }, 1500);
            }

            function displayResults(result) {
                const analysisContent = document.getElementById('analysisContent');
                const briefContent = document.getElementById('briefContent');
                const sourcingContent = document.getElementById('sourcingContent');

                // Display analysis results
                analysisContent.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="font-causten">Product: ${result.analysis.product_name || 'Unknown'}</h5>
                            <p class="font-roboto-serif">${result.analysis.description || 'No description available'}</p>
                            <p class="font-roboto-serif"><strong>Category:</strong> ${result.analysis.category || 'Food Product'}</p>
                            <p class="font-roboto-serif"><strong>Confidence:</strong> ${(result.analysis.confidence_score * 100).toFixed(1)}%</p>
                        </div>
                        <div class="col-md-6">
                            <h6 class="font-causten">Tags:</h6>
                            <div class="d-flex flex-wrap gap-1">
                                ${(result.analysis.tags || []).map(tag => `<span class="badge bg-light text-dark">${tag}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                `;

                // Display product brief
                if (result.brief) {
                    briefContent.innerHTML = `
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="font-causten">Specifications:</h6>
                                <ul class="font-roboto-serif">
                                    ${Object.entries(result.brief.specifications || {}).map(([key, value]) => 
                                        `<li><strong>${key}:</strong> ${value}</li>`
                                    ).join('')}
                                </ul>
                                <h6 class="font-causten mt-3">Quality Standards:</h6>
                                <div class="d-flex flex-wrap gap-1">
                                    ${(result.brief.quality_standards || []).map(standard => 
                                        `<span class="badge bg-success">${standard}</span>`
                                    ).join('')}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6 class="font-causten">Packaging Options:</h6>
                                <div class="d-flex flex-wrap gap-1 mb-3">
                                    ${(result.brief.packaging_options || []).map(size => 
                                        `<span class="badge bg-primary">${size}</span>`
                                    ).join('')}
                                </div>
                                <h6 class="font-causten">Price Range:</h6>
                                <p class="font-roboto-serif">
                                    $${result.brief.estimated_price_range?.min || 0} - $${result.brief.estimated_price_range?.max || 0} 
                                    per ${result.brief.estimated_price_range?.currency || 'USD'}
                                </p>
                                <h6 class="font-causten">Target Market:</h6>
                                <p class="font-roboto-serif">${result.brief.target_market || 'B2B Food Industry'}</p>
                            </div>
                        </div>
                    `;
                } else {
                    briefContent.innerHTML = '<p class="font-roboto-serif text-muted">No brief available</p>';
                }

                // Display sourcing recommendations
                if (result.similar_products && result.similar_products.length > 0) {
                    sourcingContent.innerHTML = `
                        <div class="row">
                            ${result.similar_products.map(product => `
                                <div class="col-md-6 col-lg-4 mb-3">
                                    <div class="card h-100">
                                        <div class="card-body">
                                            <h6 class="font-causten">${product.name}</h6>
                                            <p class="font-roboto-serif text-muted mb-1">${product.supplier}</p>
                                            <p class="font-roboto-serif mb-1"><strong>Price:</strong> $${product.price}</p>
                                            <p class="font-roboto-serif mb-2"><strong>Rating:</strong> ${product.rating}★</p>
                                            <span class="badge bg-success">${product.availability}</span>
                                        </div>
                                        <div class="card-footer bg-transparent">
                                            <button class="btn btn-sm btn-primary w-100">Contact Supplier</button>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                } else {
                    sourcingContent.innerHTML = '<p class="font-roboto-serif text-muted">No similar products found</p>';
                }

                resultsArea.classList.remove('d-none');
            }

            function showLoading() {
                loadingSpinner.classList.remove('d-none');
                resultsArea.classList.add('d-none');
            }

            function hideLoading() {
                loadingSpinner.classList.add('d-none');
            }

            function showError(message) {
                hideLoading();
                alert(message);
            }
        </script>
    </body>
    </html>
    """)

@router.post("/analyze-image")
async def analyze_product_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyze product image using AI"""
    try:
        # Save uploaded image temporarily
        image_content = await image.read()
        image_url = f"/uploads/{image.filename}"
        
        # Analyze image using AI service
        analysis_result = await product_analysis_service.analyze_product_image(image_url)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Generate product brief
        brief_result = await product_analysis_service.generate_product_brief(analysis_result)
        
        # Search for similar products
        similar_products = await product_analysis_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")

@router.post("/analyze-text")
async def analyze_product_text(
    search_text: str = Form(...),
    db: Session = Depends(get_db)
):
    """Analyze product text using AI"""
    try:
        # Analyze text using AI service
        analysis_result = await product_analysis_service.analyze_text_search(search_text)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Generate product brief
        brief_result = await product_analysis_service.generate_product_brief(analysis_result)
        
        # Search for similar products
        similar_products = await product_analysis_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products
        }
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze text")

@router.get("/history")
async def get_analysis_history(db: Session = Depends(get_db)):
    """Get user's analysis history"""
    try:
        # This would fetch from the product_analyses table
        # For now, return mock data
        return {
            "success": True,
            "history": [
                {
                    "id": 1,
                    "product_name": "Organic Dried Cranberries",
                    "analysis_type": "image",
                    "created_at": "2024-01-15T10:30:00Z",
                    "status": "completed"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching analysis history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")