"""Simplified API routes using the new database schema"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from foodxchange.database import get_db
from foodxchange.models.simplified import User, Project, Quote, Product
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for API
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[str] = None

class QuoteCreate(BaseModel):
    project_id: int
    price: float
    delivery_days: Optional[int] = None
    notes: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

# User routes
@router.get("/users/me")
def get_current_user(db: Session = Depends(get_db)):
    """Get current user profile"""
    # Simplified - in production, get from JWT token
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "company": user.company,
        "user_type": user.user_type
    }

# Project routes
@router.post("/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new RFQ/project"""
    # Get current user (simplified)
    current_user = db.query(User).filter(User.user_type.in_(["buyer", "both"])).first()
    if not current_user:
        raise HTTPException(status_code=403, detail="Only buyers can create projects")
    
    db_project = Project(
        title=project.title,
        description=project.description,
        user_id=current_user.id,
        budget_min=project.budget_min,
        budget_max=project.budget_max,
        deadline=datetime.strptime(project.deadline, "%Y-%m-%d") if project.deadline else None
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return {
        "id": db_project.id,
        "project_id": db_project.project_id,
        "title": db_project.title,
        "status": db_project.status,
        "created_at": db_project.created_at
    }

@router.get("/projects")
def list_projects(status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all projects with optional status filter"""
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.order_by(Project.created_at.desc()).limit(20).all()
    
    return [{
        "id": p.id,
        "project_id": p.project_id,
        "title": p.title,
        "status": p.status,
        "budget_range": f"${p.budget_min or 0} - ${p.budget_max or 0}",
        "deadline": p.deadline.isoformat() if p.deadline else None,
        "created_at": p.created_at.isoformat()
    } for p in projects]

# Quote routes
@router.post("/quotes")
def submit_quote(quote: QuoteCreate, db: Session = Depends(get_db)):
    """Submit a quote for a project"""
    # Get current supplier (simplified)
    current_user = db.query(User).filter(User.user_type.in_(["supplier", "both"])).first()
    if not current_user:
        raise HTTPException(status_code=403, detail="Only suppliers can submit quotes")
    
    # Check project exists and is open
    project = db.query(Project).filter(Project.id == quote.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "open":
        raise HTTPException(status_code=400, detail="Project is not accepting quotes")
    
    db_quote = Quote(
        project_id=quote.project_id,
        supplier_id=current_user.id,
        price=quote.price,
        delivery_days=quote.delivery_days,
        notes=quote.notes
    )
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    return {
        "id": db_quote.id,
        "project_id": db_quote.project_id,
        "price": db_quote.price,
        "status": db_quote.status,
        "created_at": db_quote.created_at
    }

@router.get("/projects/{project_id}/quotes")
def get_project_quotes(project_id: int, db: Session = Depends(get_db)):
    """Get all quotes for a project"""
    quotes = db.query(Quote).filter(Quote.project_id == project_id).all()
    
    return [{
        "id": q.id,
        "supplier": {
            "id": q.supplier.id,
            "name": q.supplier.name,
            "company": q.supplier.company,
            "rating": q.supplier.rating
        },
        "price": q.price,
        "delivery_days": q.delivery_days,
        "notes": q.notes,
        "status": q.status,
        "created_at": q.created_at.isoformat()
    } for q in quotes]

# Product routes
@router.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product in catalog"""
    # Get current supplier (simplified)
    current_user = db.query(User).filter(User.user_type.in_(["supplier", "both"])).first()
    if not current_user:
        raise HTTPException(status_code=403, detail="Only suppliers can add products")
    
    db_product = Product(
        supplier_id=current_user.id,
        name=product.name,
        category=product.category,
        price=product.price,
        description=product.description,
        image_url=product.image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return {
        "id": db_product.id,
        "name": db_product.name,
        "category": db_product.category,
        "price": db_product.price,
        "created_at": db_product.created_at
    }

@router.get("/products")
def list_products(category: Optional[str] = None, db: Session = Depends(get_db)):
    """List products with optional category filter"""
    query = db.query(Product).filter(Product.is_active == True)
    if category:
        query = query.filter(Product.category == category)
    
    products = query.limit(50).all()
    
    return [{
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "supplier": {
            "id": p.supplier.id,
            "name": p.supplier.name,
            "company": p.supplier.company
        },
        "image_url": p.image_url
    } for p in products]

# Simple dashboard data
@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get simple dashboard statistics"""
    # Get current user (simplified)
    current_user = db.query(User).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.is_buyer():
        # Buyer stats
        my_projects = db.query(Project).filter(Project.user_id == current_user.id).count()
        open_projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.status == "open"
        ).count()
        
        return {
            "user_type": "buyer",
            "total_projects": my_projects,
            "open_projects": open_projects,
            "reviewing_projects": db.query(Project).filter(
                Project.user_id == current_user.id,
                Project.status == "reviewing"
            ).count()
        }
    else:
        # Supplier stats
        my_quotes = db.query(Quote).filter(Quote.supplier_id == current_user.id).count()
        accepted_quotes = db.query(Quote).filter(
            Quote.supplier_id == current_user.id,
            Quote.status == "accepted"
        ).count()
        my_products = db.query(Product).filter(Product.supplier_id == current_user.id).count()
        
        return {
            "user_type": "supplier",
            "total_quotes": my_quotes,
            "accepted_quotes": accepted_quotes,
            "total_products": my_products
        }