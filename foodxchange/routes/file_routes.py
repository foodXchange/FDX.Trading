"""
File upload and management routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.blob_storage_service import blob_storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload/{container_type}")
async def upload_file(
    container_type: str,
    file: UploadFile = File(...),
    entity_id: Optional[int] = Query(None, description="Related entity ID (quote_id, order_id, etc)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file to blob storage
    
    Container types: quotes, orders, products, suppliers, emails
    """
    # Validate container type
    if container_type not in blob_storage_service.CONTAINERS:
        raise HTTPException(status_code=400, detail=f"Invalid container type: {container_type}")
    
    # Validate file size (10MB limit)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset file pointer
    
    if not blob_storage_service.validate_file_size(file_size):
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    # Prepare metadata
    metadata = {
        "uploaded_by": current_user.email,
        "user_id": str(current_user.id)
    }
    if entity_id:
        metadata["entity_id"] = str(entity_id)
    
    try:
        # Upload file
        result = await blob_storage_service.upload_file(
            file=file.file,
            filename=file.filename,
            container_type=container_type,
            company_id=current_user.company_id,
            metadata=metadata
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="File upload failed")
        
        logger.info(f"File uploaded: {file.filename} to {container_type} by user {current_user.id}")
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "blob_name": result["blob_name"],
            "container": result["container"],
            "url": result["url"],
            "sas_url": result["sas_url"],  # Temporary access URL (24 hours)
            "size": file_size
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list/{container_type}")
async def list_files(
    container_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List files in a container for the user's company"""
    
    if container_type not in blob_storage_service.CONTAINERS:
        raise HTTPException(status_code=400, detail=f"Invalid container type: {container_type}")
    
    try:
        files = await blob_storage_service.list_files(
            container_type=container_type,
            company_id=current_user.company_id
        )
        
        # Add SAS URLs for each file
        for file in files:
            file["sas_url"] = blob_storage_service.generate_sas_url(
                container_name=blob_storage_service.CONTAINERS[container_type],
                blob_name=file["name"],
                hours=1  # 1 hour access
            )
        
        return {
            "container": container_type,
            "count": len(files),
            "files": files
        }
        
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.get("/download/{container_type}/{blob_name:path}")
async def get_download_url(
    container_type: str,
    blob_name: str,
    hours: int = Query(1, ge=1, le=24, description="Hours until URL expires"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a temporary download URL for a file"""
    
    if container_type not in blob_storage_service.CONTAINERS:
        raise HTTPException(status_code=400, detail=f"Invalid container type: {container_type}")
    
    # Verify the file belongs to user's company
    if not blob_name.startswith(f"company_{current_user.company_id}/"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    container_name = blob_storage_service.CONTAINERS[container_type]
    
    sas_url = blob_storage_service.generate_sas_url(
        container_name=container_name,
        blob_name=blob_name,
        hours=hours
    )
    
    if not sas_url:
        raise HTTPException(status_code=500, detail="Failed to generate download URL")
    
    return {
        "download_url": sas_url,
        "expires_in_hours": hours,
        "filename": blob_name.split("/")[-1]
    }


@router.delete("/{container_type}/{blob_name:path}")
async def delete_file(
    container_type: str,
    blob_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file from blob storage"""
    
    if container_type not in blob_storage_service.CONTAINERS:
        raise HTTPException(status_code=400, detail=f"Invalid container type: {container_type}")
    
    # Verify the file belongs to user's company
    if not blob_name.startswith(f"company_{current_user.company_id}/"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    container_name = blob_storage_service.CONTAINERS[container_type]
    
    try:
        success = await blob_storage_service.delete_file(
            container_name=container_name,
            blob_name=blob_name
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"File deleted: {blob_name} by user {current_user.id}")
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.post("/quotes/{quote_id}/upload")
async def upload_quote_document(
    quote_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for a specific quote"""
    
    # Verify quote exists and belongs to user's company
    from app.models.quote import Quote
    quote = db.query(Quote).filter_by(id=quote_id).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check access (either buyer or supplier)
    from app.models.rfq import RFQ
    rfq = db.query(RFQ).filter_by(id=quote.rfq_id).first()
    
    if rfq.company_id != current_user.company_id and quote.supplier_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Upload file
    metadata = {
        "uploaded_by": current_user.email,
        "user_id": str(current_user.id),
        "quote_id": str(quote_id),
        "rfq_id": str(quote.rfq_id)
    }
    
    try:
        result = await blob_storage_service.upload_file(
            file=file.file,
            filename=file.filename,
            container_type="quotes",
            company_id=current_user.company_id,
            metadata=metadata
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="File upload failed")
        
        # Update quote with document URL
        quote.document_url = result["url"]
        quote.document_blob_name = result["blob_name"]
        db.commit()
        
        logger.info(f"Quote document uploaded: {file.filename} for quote {quote_id}")
        
        return {
            "message": "Quote document uploaded successfully",
            "filename": file.filename,
            "url": result["url"],
            "sas_url": result["sas_url"]
        }
        
    except Exception as e:
        logger.error(f"Quote document upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/orders/{order_id}/upload")
async def upload_order_document(
    order_id: int,
    file: UploadFile = File(...),
    document_type: str = Query(..., description="Document type: po, invoice, delivery_note, other"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for a specific order"""
    
    # Verify order exists and user has access
    from app.models.order import Order
    order = db.query(Order).filter_by(id=order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.buyer_company_id != current_user.company_id and order.supplier_company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Upload file
    metadata = {
        "uploaded_by": current_user.email,
        "user_id": str(current_user.id),
        "order_id": str(order_id),
        "document_type": document_type,
        "order_number": order.order_number
    }
    
    try:
        result = await blob_storage_service.upload_file(
            file=file.file,
            filename=file.filename,
            container_type="orders",
            company_id=current_user.company_id,
            metadata=metadata
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="File upload failed")
        
        # Store document reference (you might want to create an OrderDocument model)
        # For now, we'll store in order's additional_data JSON field
        if not order.additional_data:
            order.additional_data = {}
        
        if "documents" not in order.additional_data:
            order.additional_data["documents"] = []
        
        order.additional_data["documents"].append({
            "type": document_type,
            "filename": file.filename,
            "blob_name": result["blob_name"],
            "url": result["url"],
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by": current_user.email
        })
        
        db.commit()
        
        logger.info(f"Order document uploaded: {file.filename} for order {order_id}")
        
        return {
            "message": "Order document uploaded successfully",
            "filename": file.filename,
            "document_type": document_type,
            "url": result["url"],
            "sas_url": result["sas_url"]
        }
        
    except Exception as e:
        logger.error(f"Order document upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")