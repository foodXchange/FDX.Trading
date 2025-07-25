"""
Routes for Web Scraping functionality
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.agents.supplier_web_scraper_agent import web_scraping_service, SupplierWebScraperAgent

router = APIRouter(prefix="/api/scraper", tags=["web-scraper"])


@router.post("/scrape/supplier/{supplier_id}")
async def scrape_supplier(
    supplier_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Scrape a single supplier's website for products"""
    
    # Check if supplier exists
    from app.models.supplier import Supplier
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    if not supplier.website:
        raise HTTPException(status_code=400, detail="Supplier has no website configured")
    
    # Run scraping in background
    background_tasks.add_task(
        scrape_supplier_background,
        supplier_id,
        current_user.id
    )
    
    return {
        "status": "started",
        "message": f"Web scraping started for {supplier.name}",
        "supplier_id": supplier_id,
        "website": supplier.website,
        "note": "Scraping includes 7-second delays between pages for compliance"
    }


async def scrape_supplier_background(supplier_id: int, user_id: int):
    """Background task to scrape supplier website"""
    try:
        result = await web_scraping_service.scrape_single_supplier(supplier_id)
        
        # Log the result
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            from app.models.activity_log import ActivityLog
            log = ActivityLog(
                user_id=user_id,
                action="web_scrape_completed",
                details=result,
                entity_type="supplier",
                entity_id=supplier_id
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
            
    except Exception as e:
        # Log error
        import logging
        logging.error(f"Web scraping failed for supplier {supplier_id}: {str(e)}")


@router.get("/scrape/status")
async def get_scraping_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current status of web scraping service"""
    return {
        "is_running": web_scraping_service.is_running,
        "interval_seconds": web_scraping_service.scraping_interval,
        "interval_hours": web_scraping_service.scraping_interval / 3600
    }


@router.post("/scrape/start-service")
async def start_scraping_service(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start the automated web scraping service"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if web_scraping_service.is_running:
        return {
            "status": "already_running",
            "message": "Web scraping service is already running"
        }
    
    background_tasks.add_task(web_scraping_service.start)
    
    return {
        "status": "started",
        "message": "Web scraping service started",
        "interval": f"Will scrape all suppliers every {web_scraping_service.scraping_interval / 3600} hours"
    }


@router.post("/scrape/stop-service")
async def stop_scraping_service(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Stop the automated web scraping service"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await web_scraping_service.stop()
    
    return {
        "status": "stopped",
        "message": "Web scraping service stopped"
    }


@router.post("/scrape/test/{supplier_id}")
async def test_scrape_supplier(
    supplier_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test web scraping for a supplier (limited pages)"""
    
    # Check if supplier exists
    from app.models.supplier import Supplier
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    if not supplier.website:
        raise HTTPException(status_code=400, detail="Supplier has no website configured")
    
    # Create scraper agent
    agent = SupplierWebScraperAgent(db)
    
    # Analyze site structure
    site_map = await agent._analyze_site_structure(supplier.website)
    
    return {
        "supplier": {
            "id": supplier.id,
            "name": supplier.name,
            "website": supplier.website
        },
        "site_analysis": {
            "base_url": site_map.get("base_url"),
            "detected_language": site_map.get("detected_language"),
            "product_urls_found": len(site_map.get("product_urls", [])),
            "sample_urls": site_map.get("product_urls", [])[:limit],
            "structured_products": len(site_map.get("structured_products", []))
        },
        "message": f"Found {len(site_map.get('product_urls', []))} potential product pages"
    }


@router.get("/scrape/history/{supplier_id}")
async def get_scraping_history(
    supplier_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get scraping history for a supplier"""
    
    from app.models.supplier import Supplier
    from app.models.product import Product
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Get product count
    product_count = db.query(Product).filter(
        Product.supplier_id == supplier_id
    ).count()
    
    # Get recent products
    recent_products = db.query(Product).filter(
        Product.supplier_id == supplier_id
    ).order_by(Product.created_at.desc()).limit(limit).all()
    
    return {
        "supplier": {
            "id": supplier.id,
            "name": supplier.name,
            "website": supplier.website,
            "last_scraped": supplier.last_scraped.isoformat() if supplier.last_scraped else None
        },
        "statistics": {
            "total_products": product_count,
            "languages_found": list(set(p.language for p in recent_products if p.language))
        },
        "recent_products": [
            {
                "id": p.id,
                "name": p.name,
                "original_name": p.original_name,
                "category": p.category,
                "price": p.price,
                "currency": p.currency,
                "created_at": p.created_at.isoformat()
            }
            for p in recent_products
        ]
    }


def include_scraper_routes(app):
    """Include web scraper routes in the main app"""
    app.include_router(router)