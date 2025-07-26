"""
Product catalog management routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Form, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import uuid

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.company import Company
from app.services.simple_notification_service import NotificationService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/")
async def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    supplier_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(True),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("name", regex="^(name|price|created_at|stock)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get products with advanced filtering"""
    # Base query
    query = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.company)
    )
    
    # Filter by supplier if user is a supplier
    if current_user.role == "supplier" and current_user.company_id:
        supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
        if supplier:
            query = query.filter(Product.supplier_id == supplier.id)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.sku.ilike(search_term)
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if supplier_id is not None:
        query = query.filter(Product.supplier_id == supplier_id)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    # Get total count
    total_count = query.count()
    
    # Apply sorting
    if sort_by == "name":
        query = query.order_by(Product.name.asc() if order == "asc" else Product.name.desc())
    elif sort_by == "price":
        query = query.order_by(Product.price.asc() if order == "asc" else Product.price.desc())
    elif sort_by == "stock":
        query = query.order_by(Product.stock_quantity.asc() if order == "asc" else Product.stock_quantity.desc())
    else:
        query = query.order_by(Product.created_at.desc() if order == "desc" else Product.created_at.asc())
    
    # Apply pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    return {
        "items": [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "sku": product.sku,
                "category": product.category,
                "price": float(product.price) if product.price else None,
                "unit": product.unit,
                "stock_quantity": float(product.stock_quantity) if product.stock_quantity else None,
                "min_order_quantity": float(product.min_order_quantity) if product.min_order_quantity else 1,
                "supplier_id": product.supplier_id,
                "supplier_name": product.supplier.name if product.supplier else None,
                "is_active": product.is_active,
                "images": product.images if product.images else [],
                "created_at": product.created_at.isoformat() if product.created_at else None
            }
            for product in products
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit
        }
    }


@router.post("/")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    sku: str = Form(None),
    category: str = Form(...),
    price: float = Form(...),
    unit: str = Form(...),
    stock_quantity: Optional[float] = Form(None),
    min_order_quantity: Optional[float] = Form(1),
    specifications: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product (suppliers only)"""
    # Verify user is a supplier
    if current_user.role != "supplier" or not current_user.company_id:
        raise HTTPException(status_code=403, detail="Only suppliers can create products")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # Generate SKU if not provided
    if not sku:
        sku = f"{supplier.id}-{name[:3].upper()}-{str(uuid.uuid4())[:8]}"
    
    # Check if SKU already exists
    existing = db.query(Product).filter(Product.sku == sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    # Parse specifications
    specs = json.loads(specifications) if specifications else {}
    
    # Create product
    product = Product(
        supplier_id=supplier.id,
        company_id=current_user.company_id,
        name=name,
        description=description,
        sku=sku,
        category=category,
        price=price,
        unit=unit,
        stock_quantity=stock_quantity,
        min_order_quantity=min_order_quantity,
        specifications=specs,
        is_active=True
    )
    
    # TODO: Handle image uploads
    # For now, store empty array
    product.images = []
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return {
        "id": product.id,
        "sku": product.sku,
        "message": "Product created successfully"
    }


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product details"""
    product = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.company)
    ).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "sku": product.sku,
        "category": product.category,
        "price": float(product.price) if product.price else None,
        "unit": product.unit,
        "stock_quantity": float(product.stock_quantity) if product.stock_quantity else None,
        "min_order_quantity": float(product.min_order_quantity) if product.min_order_quantity else 1,
        "specifications": product.specifications,
        "images": product.images if product.images else [],
        "is_active": product.is_active,
        "supplier": {
            "id": product.supplier.id,
            "name": product.supplier.name,
            "company_name": product.supplier.company_name if product.supplier else None,
            "rating": float(product.supplier.rating) if product.supplier and product.supplier.rating else None
        },
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None
    }


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    unit: Optional[str] = Form(None),
    stock_quantity: Optional[float] = Form(None),
    min_order_quantity: Optional[float] = Form(None),
    specifications: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update product (supplier only)"""
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify ownership
    if current_user.role == "supplier" and current_user.company_id:
        supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
        if not supplier or product.supplier_id != supplier.id:
            raise HTTPException(status_code=403, detail="You can only update your own products")
    elif current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update fields
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if category is not None:
        product.category = category
    if price is not None:
        product.price = price
    if unit is not None:
        product.unit = unit
    if stock_quantity is not None:
        product.stock_quantity = stock_quantity
    if min_order_quantity is not None:
        product.min_order_quantity = min_order_quantity
    if specifications is not None:
        product.specifications = json.loads(specifications)
    if is_active is not None:
        product.is_active = is_active
    
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return {"message": "Product updated successfully"}


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete product (soft delete by deactivating)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify ownership
    if current_user.role == "supplier" and current_user.company_id:
        supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
        if not supplier or product.supplier_id != supplier.id:
            raise HTTPException(status_code=403, detail="You can only delete your own products")
    elif current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Soft delete by deactivating
    product.is_active = False
    product.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Product deleted successfully"}


@router.post("/{product_id}/stock")
async def update_stock(
    product_id: int,
    quantity: float = Form(...),
    operation: str = Form("set", regex="^(set|add|subtract)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update product stock quantity"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify ownership
    if current_user.role == "supplier" and current_user.company_id:
        supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
        if not supplier or product.supplier_id != supplier.id:
            raise HTTPException(status_code=403, detail="You can only update stock for your own products")
    elif current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update stock based on operation
    if operation == "set":
        product.stock_quantity = quantity
    elif operation == "add":
        product.stock_quantity = (product.stock_quantity or 0) + quantity
    elif operation == "subtract":
        new_quantity = (product.stock_quantity or 0) - quantity
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        product.stock_quantity = new_quantity
    
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return {
        "message": f"Stock {operation} successful",
        "new_stock_quantity": product.stock_quantity
    }


@router.get("/supplier/catalog")
async def get_supplier_catalog(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier's product catalog with statistics"""
    if current_user.role != "supplier" or not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # Get all products
    products = db.query(Product).filter(Product.supplier_id == supplier.id).all()
    
    # Calculate statistics
    total_products = len(products)
    active_products = len([p for p in products if p.is_active])
    out_of_stock = len([p for p in products if p.stock_quantity == 0])
    low_stock = len([p for p in products if p.stock_quantity and p.stock_quantity < 10])
    
    # Get categories
    categories = {}
    for product in products:
        if product.category:
            categories[product.category] = categories.get(product.category, 0) + 1
    
    # Get recent products
    recent_products = sorted(products, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
    
    return {
        "statistics": {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": total_products - active_products,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "total_value": sum(p.price * (p.stock_quantity or 0) for p in products if p.price)
        },
        "categories": [
            {"name": cat, "count": count}
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)
        ],
        "recent_products": [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "price": float(p.price) if p.price else None,
                "stock": p.stock_quantity,
                "is_active": p.is_active,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in recent_products
        ]
    }


@router.post("/bulk-import")
async def bulk_import_products(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk import products from CSV file"""
    if current_user.role != "supplier" or not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # TODO: Implement CSV parsing and bulk import
    # For now, return placeholder response
    
    return {
        "message": "Bulk import feature coming soon",
        "file_name": file.filename
    }


@router.get("/categories")
async def get_product_categories(
    db: Session = Depends(get_db)
):
    """Get all available product categories"""
    # In a real implementation, this would come from a categories table
    categories = [
        {"value": "fresh_produce", "label": "Fresh Produce", "icon": "🥬"},
        {"value": "meat_poultry", "label": "Meat & Poultry", "icon": "🍖"},
        {"value": "dairy_eggs", "label": "Dairy & Eggs", "icon": "🥛"},
        {"value": "grains_cereals", "label": "Grains & Cereals", "icon": "🌾"},
        {"value": "beverages", "label": "Beverages", "icon": "🥤"},
        {"value": "snacks_confectionery", "label": "Snacks & Confectionery", "icon": "🍫"},
        {"value": "frozen_foods", "label": "Frozen Foods", "icon": "🧊"},
        {"value": "canned_goods", "label": "Canned Goods", "icon": "🥫"},
        {"value": "condiments_sauces", "label": "Condiments & Sauces", "icon": "🍯"},
        {"value": "bakery", "label": "Bakery Products", "icon": "🍞"},
        {"value": "seafood", "label": "Seafood", "icon": "🐟"},
        {"value": "oils_fats", "label": "Oils & Fats", "icon": "🫒"}
    ]
    
    return categories


def include_product_routes(app):
    """Include product routes in the main app"""
    app.include_router(router)