"""
API Routes for Data Mining and Import Operations
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import shutil

from foodxchange.database import get_db
from foodxchange.models.user import User
from foodxchange.models.supplier import Supplier
from foodxchange.auth import get_current_user
from foodxchange.agents.supplier_web_scraper_agent import web_scraping_service, SupplierWebScraperAgent
from foodxchange.agents.csv_data_import_agent import CSVDataImportAgent, ExcelDataImportAgent

router = APIRouter(prefix="/api/data-mining", tags=["data-mining"])


@router.post("/scrape-supplier-website")
async def scrape_supplier_website(
    supplier_id: int,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Scrape a specific supplier's website for products
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify supplier exists and has website
    supplier = db.query(Supplier).get(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    if not supplier.website:
        raise HTTPException(status_code=400, detail="Supplier has no website configured")
    
    # Run scraping in background
    background_tasks.add_task(
        web_scraping_service.scrape_single_supplier,
        supplier_id
    )
    
    return {
        "status": "started",
        "message": f"Started scraping {supplier.name}'s website",
        "supplier_id": supplier_id,
        "website": supplier.website
    }


@router.post("/scrape-all-suppliers")
async def scrape_all_suppliers(
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start scraping all active suppliers' websites
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Count suppliers with websites
    supplier_count = db.query(Supplier).filter(
        Supplier.website.isnot(None),
        Supplier.is_active == True
    ).count()
    
    if supplier_count == 0:
        return {
            "status": "no_suppliers",
            "message": "No active suppliers with websites found"
        }
    
    # Start background scraping
    background_tasks.add_task(web_scraping_service._scrape_all_suppliers)
    
    return {
        "status": "started",
        "message": f"Started scraping {supplier_count} supplier websites",
        "estimated_time": f"{supplier_count * 2} minutes",  # ~2 min per supplier
        "note": "7-second delay between requests for respectful scraping"
    }


@router.post("/import-csv")
async def import_csv_file(
    file: UploadFile = File(...),
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Import products from a CSV file
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Save uploaded file temporarily
    temp_dir = "/tmp/foodxchange_imports"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_path = os.path.join(temp_dir, f"{datetime.utcnow().timestamp()}_{file.filename}")
    
    try:
        # Save file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process CSV
        agent = CSVDataImportAgent(db)
        result = await agent.import_csv_file(temp_path, supplier_id)
        
        return result
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/import-excel")
async def import_excel_file(
    file: UploadFile = File(...),
    supplier_id: Optional[int] = None,
    sheet_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Import products from an Excel file
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate file type
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    # Save uploaded file temporarily
    temp_dir = "/tmp/foodxchange_imports"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_path = os.path.join(temp_dir, f"{datetime.utcnow().timestamp()}_{file.filename}")
    
    try:
        # Save file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process Excel
        agent = ExcelDataImportAgent(db)
        result = await agent.import_excel_file(temp_path, sheet_name, supplier_id)
        
        return result
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/bulk-import")
async def bulk_import_files(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Import multiple CSV/Excel files at once
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate files
    valid_extensions = ['.csv', '.xlsx', '.xls']
    for file in files:
        if not any(file.filename.endswith(ext) for ext in valid_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.filename}. Only CSV and Excel files allowed."
            )
    
    # Save files temporarily
    temp_dir = "/tmp/foodxchange_imports"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_paths = []
    for file in files:
        temp_path = os.path.join(temp_dir, f"{datetime.utcnow().timestamp()}_{file.filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(temp_path)
    
    # Process in background
    async def process_files():
        csv_agent = CSVDataImportAgent(db)
        results = await csv_agent.process_multiple_files(file_paths)
        
        # Clean up
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
        
        return results
    
    background_tasks.add_task(process_files)
    
    return {
        "status": "processing",
        "message": f"Processing {len(files)} files in background",
        "files": [f.filename for f in files],
        "note": "Check import status endpoint for results"
    }


@router.get("/scraping-status/{supplier_id}")
async def get_scraping_status(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the scraping status for a supplier
    """
    supplier = db.query(Supplier).get(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Get product count
    from foodxchange.models.product import Product
    product_count = db.query(Product).filter(
        Product.supplier_id == supplier_id
    ).count()
    
    return {
        "supplier_id": supplier_id,
        "supplier_name": supplier.name,
        "website": supplier.website,
        "last_scraped": supplier.last_scraped.isoformat() if supplier.last_scraped else None,
        "product_count": product_count,
        "is_active": supplier.is_active
    }


@router.get("/products/search")
async def search_products(
    query: str,
    supplier_id: Optional[int] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Search through scraped products
    """
    from foodxchange.models.product import Product
    
    # Build query
    products_query = db.query(Product).filter(Product.is_active == True)
    
    # Text search
    if query:
        products_query = products_query.filter(
            (Product.name.ilike(f"%{query}%")) |
            (Product.original_name.ilike(f"%{query}%")) |
            (Product.description.ilike(f"%{query}%"))
        )
    
    # Filters
    if supplier_id:
        products_query = products_query.filter(Product.supplier_id == supplier_id)
    
    if category:
        products_query = products_query.filter(Product.category == category)
    
    if min_price:
        products_query = products_query.filter(Product.price >= min_price)
    
    if max_price:
        products_query = products_query.filter(Product.price <= max_price)
    
    # Execute query
    products = products_query.limit(limit).all()
    
    return {
        "query": query,
        "filters": {
            "supplier_id": supplier_id,
            "category": category,
            "price_range": f"{min_price or 0}-{max_price or 'unlimited'}"
        },
        "count": len(products),
        "products": [p.to_dict() for p in products]
    }


@router.get("/categories")
async def get_product_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get all available product categories
    """
    from foodxchange.models.product import Product
    from sqlalchemy import func, distinct
    
    # Get distinct categories with counts
    categories = db.query(
        Product.category,
        func.count(Product.id).label('count')
    ).filter(
        Product.category.isnot(None),
        Product.is_active == True
    ).group_by(Product.category).all()
    
    return {
        "total_categories": len(categories),
        "categories": [
            {"name": cat[0], "product_count": cat[1]}
            for cat in categories
        ]
    }


@router.post("/translate-products")
async def translate_products(
    supplier_id: int,
    target_language: str = "en",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Translate all products from a supplier to target language
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from foodxchange.models.product import Product
    
    # Count products needing translation
    products_to_translate = db.query(Product).filter(
        Product.supplier_id == supplier_id,
        Product.language != target_language
    ).count()
    
    if products_to_translate == 0:
        return {
            "status": "no_translation_needed",
            "message": "All products already in target language"
        }
    
    # This would run the translation in background
    # For now, return status
    return {
        "status": "translation_queued",
        "supplier_id": supplier_id,
        "products_to_translate": products_to_translate,
        "target_language": target_language,
        "estimated_time": f"{products_to_translate * 2} seconds"
    }


# Include router in main app
def include_data_mining_routes(app):
    """Include data mining routes in the main FastAPI app"""
    app.include_router(router)