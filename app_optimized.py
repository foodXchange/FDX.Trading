"""
FDX.trading - Optimized Application
Single source of truth for the application
"""

import os
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection pool
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global db_pool
    try:
        # Initialize database pool
        db_pool = psycopg2.pool.ThreadedConnectionPool(
            1, 20,
            os.getenv('DATABASE_URL')
        )
        logger.info("Database pool initialized")
        yield
    finally:
        # Cleanup
        if db_pool:
            db_pool.closeall()
            logger.info("Database pool closed")

# Create FastAPI app
app = FastAPI(
    title="FDX.trading",
    description="Optimized Food Exchange Platform",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for validation
class SupplierFilter(BaseModel):
    search: Optional[str] = None
    country: Optional[str] = None
    limit: int = Query(default=100, le=1000)
    offset: int = Query(default=0, ge=0)

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

# Database context manager
@contextmanager
def get_db_cursor():
    """Get database cursor with automatic cleanup"""
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db_pool.putconn(conn)

# Dependency for user authentication (placeholder)
async def get_current_user(request: Request) -> dict:
    """Get current user from session or JWT"""
    # TODO: Implement proper authentication
    return {"email": "user@example.com", "id": 1}

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "FDX.trading"}
    )

@app.get("/api/suppliers")
async def get_suppliers(
    filters: SupplierFilter = Depends(),
    user: dict = Depends(get_current_user)
):
    """Get suppliers with pagination and filtering"""
    try:
        with get_db_cursor() as cursor:
            # Build query with filters
            query = """
                SELECT id, supplier_name, company_name, country, 
                       products, email, verified, rating
                FROM suppliers
                WHERE 1=1
            """
            params = []
            
            if filters.search:
                query += " AND (supplier_name ILIKE %s OR products ILIKE %s)"
                search_term = f"%{filters.search}%"
                params.extend([search_term, search_term])
            
            if filters.country:
                query += " AND country = %s"
                params.append(filters.country)
            
            # Add pagination
            query += " ORDER BY rating DESC, supplier_name"
            query += " LIMIT %s OFFSET %s"
            params.extend([filters.limit, filters.offset])
            
            cursor.execute(query, params)
            suppliers = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) as total FROM suppliers WHERE 1=1"
            count_params = []
            
            if filters.search:
                count_query += " AND (supplier_name ILIKE %s OR products ILIKE %s)"
                count_params.extend([search_term, search_term])
            
            if filters.country:
                count_query += " AND country = %s"
                count_params.append(filters.country)
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()['total']
            
            return {
                "suppliers": suppliers,
                "total": total,
                "limit": filters.limit,
                "offset": filters.offset
            }
    
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/projects")
async def create_project(
    project: ProjectCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new project"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO projects (project_name, description, user_email, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id, project_name, description, created_at
                """,
                (project.name, project.description, user['email'], datetime.now())
            )
            new_project = cursor.fetchone()
            return new_project
    
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Resource not found"}
        )
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal error: {exc}")
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    return templates.TemplateResponse(
        "500.html",
        {"request": request},
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_optimized:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )