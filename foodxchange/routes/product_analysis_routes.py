"""
Product Analysis Routes for FoodXchange
AI-powered product analysis and brief generation endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime
from pathlib import Path

# Local imports
from ..services.product_analysis_service import product_analysis_service
from ..services.document_service import document_service
from ..services.email_service import azure_email_service
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/product-analysis", tags=["Product Analysis"])

@router.get("/", response_class=HTMLResponse)
async def product_analysis_page(request: Request):
    """Product Analysis Dashboard - Using Jinja2 template"""
    # Get the directory where this file is located
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Configure Jinja2 templates
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    
    return templates.TemplateResponse("pages/product_analysis.html", {"request": request})

@router.post("/analyze-image")
async def analyze_product_image(
    image: UploadFile = File(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Analyze product image using AI"""
    try:
        # Save uploaded image temporarily
        image_content = await image.read()
        image_url = f"/uploads/{image.filename}"
        
        # Analyze image using AI service
        analysis_result = await product_analysis_service.analyze_product_image(image_url, db)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Generate product brief with ML improvements
        user_query = ""
        if product_description:
            user_query = f"Additional product information: {product_description}"
        if product_category:
            user_query += f" Category: {product_category}"
        
        brief_result = await product_analysis_service.generate_product_brief(analysis_result, user_query, db)
        
        # Search for similar products
        similar_products = await product_analysis_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        # Convert image to base64 for display
        import base64
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        image_mime_type = image.content_type or 'image/jpeg'
        data_url = f"data:{image_mime_type};base64,{image_base64}"
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products,
            "analyzed_images": [data_url]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")

@router.post("/analyze-multiple-images")
async def analyze_multiple_product_images(
    images: List[UploadFile] = File(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Analyze multiple product images using AI"""
    try:
        import os
        import uuid
        import base64
        
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="No images provided")
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        analyzed_images = []
        file_paths = []
        
        # Process each image
        for image in images:
            # Generate unique filename
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            file_paths.append(file_path)
            
            # Save file to disk
            image_content = await image.read()
            with open(file_path, "wb") as f:
                f.write(image_content)
            
            # Convert to base64 for display
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            image_mime_type = image.content_type or 'image/jpeg'
            data_url = f"data:{image_mime_type};base64,{image_base64}"
            analyzed_images.append(data_url)
        
        # For now, analyze the first image and return results
        # In a full implementation, you could analyze all images and combine results
        analysis_result = await product_analysis_service.analyze_product_image(file_paths[0], db)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Generate product brief with ML improvements
        user_query = ""
        if product_description:
            user_query = f"Additional product information: {product_description}"
        if product_category:
            user_query += f" Category: {product_category}"
        
        brief_result = await product_analysis_service.generate_product_brief(analysis_result, user_query, db)
        
        # Search for similar products
        similar_products = await product_analysis_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        # Clean up temporary files
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products,
            "analyzed_images": analyzed_images,
            "total_images_processed": len(images)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing multiple images: {e}")
        # Clean up temporary files on error
        try:
            for file_path in file_paths:
                os.remove(file_path)
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to analyze images")

@router.post("/analyze-image-url")
async def analyze_product_image_url(
    image_url: str = Form(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Analyze product image from URL using AI"""
    try:
        # Validate URL
        if not image_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid image URL")
        
        # Analyze image using AI service with ML improvements
        analysis_result = await product_analysis_service.analyze_product_image(image_url, db)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Generate product brief with ML improvements
        # Combine product description and category for better analysis
        user_query = ""
        if product_description:
            user_query = f"Additional product information: {product_description}"
        if product_category:
            user_query += f" Category: {product_category}"
        
        brief_result = await product_analysis_service.generate_product_brief(analysis_result, user_query, db)
        
        # Search for similar products
        similar_products = await product_analysis_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products,
            "image_url": image_url,
            "analyzed_images": [image_url]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image from URL")

@router.post("/analyze-multiple-urls")
async def analyze_multiple_image_urls(
    image_urls: str = Form(...),  # JSON array of URLs
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Analyze multiple image URLs using AI"""
    try:
        # Parse JSON array of URLs
        urls = json.loads(image_urls)
        if not urls or len(urls) == 0:
            raise HTTPException(status_code=400, detail="No URLs provided")
        
        # Validate URLs
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                raise HTTPException(status_code=400, detail=f"Invalid URL: {url}")
        
        # Analyze first image (in a full implementation, you could analyze all images)
        analysis_result = await product_analysis_service.analyze_product_image(urls[0], db)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Generate product brief with ML improvements
        user_query = ""
        if product_description:
            user_query = f"Additional product information: {product_description}"
        if product_category:
            user_query += f" Category: {product_category}"
        
        brief_result = await product_analysis_service.generate_product_brief(analysis_result, user_query, db)
        
        # Search for similar products
        similar_products = await product_analysis_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products,
            "analyzed_images": urls,
            "total_images_processed": len(urls)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing multiple URLs: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze URLs")

@router.post("/save-field-edit")
async def save_field_edit(
    sessionId: str = Form(...),
    fieldName: str = Form(...),
    section: str = Form(...),
    oldValue: str = Form(...),
    newValue: str = Form(...),
    original_analysis: str = Form(...),
    original_brief: str = Form(...),
    product_index: Optional[int] = Form(None),
    supplier_index: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Save field edit for ML training"""
    try:
        # Parse original data
        analysis_data = json.loads(original_analysis)
        brief_data = json.loads(original_brief)
        
        # Create feedback record
        from ..models.feedback import Feedback
        feedback = Feedback(
            session_id=sessionId,
            field_name=fieldName,
            section=section,
            old_value=oldValue,
            new_value=newValue,
            analysis_data=analysis_data,
            brief_data=brief_data
        )
        
        # Update the data based on section and field
        if section == "brief" and fieldName in ["product_name", "producing_company", "brand_name", "country_of_origin", "category", "packaging_type", "product_weight", "product_appearance", "storage_conditions", "target_market", "kosher", "kosher_writings", "gluten_free", "sugar_free", "no_sugar_added"]:
            feedback.correct_product_name = newValue if fieldName == "product_name" else None
            feedback.correct_company = newValue if fieldName == "producing_company" else None
            feedback.correct_brand = newValue if fieldName == "brand_name" else None
            feedback.correct_category = newValue if fieldName == "category" else None
            feedback.correct_packaging = newValue if fieldName == "packaging_type" else None
            feedback.correct_weight = newValue if fieldName == "product_weight" else None
        elif section == "related_products" and product_index is not None:
            # Handle related products edits
            if fieldName in ["name", "unit_weight", "appearance", "packaging_type"]:
                # Update the related products in the brief data
                if "related_products" in brief_data and len(brief_data["related_products"]) > product_index:
                    brief_data["related_products"][product_index][fieldName] = newValue
                    feedback.feedback_text = f"Related product {product_index + 1} {fieldName} changed from '{oldValue}' to '{newValue}'"
        elif section == "sourcing" and supplier_index is not None:
            # Handle sourcing recommendations edits
            if fieldName in ["name", "supplier", "price", "rating", "availability"]:
                # Update the similar products in the analysis data
                if "similar_products" in analysis_data and len(analysis_data["similar_products"]) > supplier_index:
                    # Remove $ and ★ symbols for editing
                    cleanOldValue = oldValue.replace('$', '').replace('★', '').strip()
                    cleanNewValue = newValue.replace('$', '').replace('★', '').strip()
                    
                    analysis_data["similar_products"][supplier_index][fieldName] = cleanNewValue
                    feedback.feedback_text = f"Sourcing recommendation {supplier_index + 1} {fieldName} changed from '{cleanOldValue}' to '{cleanNewValue}'"
        
        # Save to database
        if db:
            db.add(feedback)
            db.commit()
        
        return {
            "success": True,
            "message": "Field edit saved successfully",
            "feedback_id": feedback.id if hasattr(feedback, 'id') else None
        }
        
    except Exception as e:
        logger.error(f"Error saving field edit: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save field edit")

@router.post("/submit-feedback")
async def submit_feedback(
    sessionId: str = Form(...),
    feedbackType: str = Form(...),
    feedbackText: str = Form(...),
    original_analysis: str = Form(...),
    original_brief: str = Form(...),
    correctProductName: Optional[str] = Form(None),
    correctBrand: Optional[str] = Form(None),
    correctCompany: Optional[str] = Form(None),
    correctCategory: Optional[str] = Form(None),
    correctPackaging: Optional[str] = Form(None),
    correctWeight: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Submit user feedback for ML training"""
    try:
        # Parse original data
        analysis_data = json.loads(original_analysis)
        brief_data = json.loads(original_brief)
        
        # Create feedback record
        from ..models.feedback import Feedback
        feedback = Feedback(
            session_id=sessionId,
            feedback_type=feedbackType,
            feedback_text=feedbackText,
            analysis_data=analysis_data,
            brief_data=brief_data,
            correct_product_name=correctProductName,
            correct_brand=correctBrand,
            correct_company=correctCompany,
            correct_category=correctCategory,
            correct_packaging=correctPackaging,
            correct_weight=correctWeight
        )
        
        # Save to database
        if db:
            db.add(feedback)
            db.commit()
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.id if hasattr(feedback, 'id') else None
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

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

@router.post("/save-project")
async def save_analysis_as_project(
    name: str = Form(...),
    description: str = Form(None),
    buyer_id: Optional[str] = Form(None),
    priority: str = Form("medium"),
    search_type: Optional[str] = Form(None),
    analysis_data: str = Form(...),
    db: Session = Depends(get_db)
):
    """Save analysis as a project"""
    try:
        import os
        from datetime import datetime
        
        # Create projects directory if it doesn't exist
        projects_dir = os.path.join(os.getcwd(), "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        # Create project data
        project_data = {
            "name": name,
            "description": description,
            "buyer_id": buyer_id if buyer_id and buyer_id != "" else None,
            "priority": priority,
            "search_type": search_type or "image",
            "analysis_data": json.loads(analysis_data),
            "created_at": datetime.now().isoformat()
        }
        
        # Save to file
        import uuid
        project_filename = f"project_{uuid.uuid4()}.json"
        project_path = os.path.join(projects_dir, project_filename)
        
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Project saved successfully",
            "project_filename": project_filename
        }
        
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        raise HTTPException(status_code=500, detail="Failed to save project")

@router.post("/generate-brief-preview")
async def generate_brief_preview(
    analysis_data: str = Form(...),
    brief_data: str = Form(...),
    custom_sections: Optional[str] = Form(None)
):
    """Generate HTML preview of product brief"""
    try:
        # Parse JSON data
        analysis = json.loads(analysis_data)
        brief = json.loads(brief_data)
        custom = json.loads(custom_sections) if custom_sections else {}
        
        # Generate HTML preview
        html_content = document_service.generate_product_brief_html(
            analysis_data=analysis,
            brief_data=brief,
            custom_sections=custom,
            editable=True
        )
        
        return {
            "success": True,
            "html_content": html_content
        }
        
    except Exception as e:
        logger.error(f"Error generating brief preview: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")

@router.post("/download-brief/{format}")
async def download_product_brief(
    format: str,
    analysis_data: str = Form(...),
    brief_data: str = Form(...),
    custom_sections: Optional[str] = Form(None),
    include_images: Optional[bool] = Form(True)
):
    """Download product brief in specified format"""
    try:
        # Validate format
        if format not in ['docx', 'pdf', 'html']:
            raise HTTPException(status_code=400, detail="Invalid format. Supported formats: docx, pdf, html")
        
        # Parse JSON data
        analysis = json.loads(analysis_data)
        brief = json.loads(brief_data)
        custom = json.loads(custom_sections) if custom_sections else {}
        
        if format == 'docx':
            # Generate DOCX
            doc_buffer = document_service.generate_product_brief_docx(
                analysis_data=analysis,
                brief_data=brief,
                custom_sections=custom,
                include_images=include_images
            )
            
            filename = f"product_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            return StreamingResponse(
                doc_buffer,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        elif format == 'pdf':
            # Generate HTML first
            html_content = document_service.generate_product_brief_html(
                analysis_data=analysis,
                brief_data=brief,
                custom_sections=custom,
                editable=False
            )
            
            # Convert to PDF
            pdf_buffer = document_service.convert_to_pdf(html_content)
            
            filename = f"product_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        else:  # HTML
            # Generate HTML
            html_content = document_service.generate_product_brief_html(
                analysis_data=analysis,
                brief_data=brief,
                custom_sections=custom,
                editable=False
            )
            
            # Create buffer
            html_buffer = io.BytesIO(html_content.encode('utf-8'))
            
            filename = f"product_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            return StreamingResponse(
                html_buffer,
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except Exception as e:
        logger.error(f"Error downloading brief: {e}")
        raise HTTPException(status_code=500, detail="Failed to download brief")

@router.post("/email-brief")
async def email_product_brief(
    recipient_emails: str = Form(...),  # JSON array of emails
    subject: str = Form(...),
    message: Optional[str] = Form(None),
    analysis_data: str = Form(...),
    brief_data: str = Form(...),
    custom_sections: Optional[str] = Form(None),
    include_attachments: Optional[bool] = Form(True)
):
    """Email product brief to recipients"""
    try:
        # Parse JSON data
        emails = json.loads(recipient_emails)
        analysis = json.loads(analysis_data)
        brief = json.loads(brief_data)
        custom = json.loads(custom_sections) if custom_sections else {}
        
        # Generate email content
        product_name = brief.get('product_name', 'Product')
        brief_summary = message or f"Product brief for {product_name}"
        
        html_body = azure_email_service.create_product_brief_email_html(
            recipient_name="Valued Partner",
            product_name=product_name,
            brief_summary=brief_summary,
            sender_name="FoodXchange Team"
        )
        
        text_body = azure_email_service.create_product_brief_email_text(
            recipient_name="Valued Partner",
            product_name=product_name,
            brief_summary=brief_summary,
            sender_name="FoodXchange Team"
        )
        
        # Prepare attachments
        attachments = []
        if include_attachments:
            # Generate DOCX attachment
            doc_buffer = document_service.generate_product_brief_docx(
                analysis_data=analysis,
                brief_data=brief,
                custom_sections=custom,
                include_images=True
            )
            
            attachments.append({
                'name': f"{product_name.replace(' ', '_')}_Brief.docx",
                'content': doc_buffer.getvalue(),
                'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            })
        
        # Send email
        result = await azure_email_service.send_product_brief(
            recipient_emails=emails,
            subject=subject,
            body_html=html_body,
            body_text=text_body,
            attachments=attachments
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error emailing brief: {e}")
        raise HTTPException(status_code=500, detail="Failed to email brief")

@router.post("/generate-multi-brief")
async def generate_multi_product_brief(
    products: str = Form(...),  # JSON array of products
    format: str = Form('docx'),
    custom_sections: Optional[str] = Form(None)
):
    """Generate brief for multiple products"""
    try:
        # Parse JSON data
        product_list = json.loads(products)
        custom = json.loads(custom_sections) if custom_sections else {}
        
        # Generate multi-product brief
        doc_buffer = document_service.generate_multi_product_brief(
            products=product_list,
            format=format,
            custom_sections=custom
        )
        
        filename = f"multi_product_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if format == 'docx' else "application/pdf"
        
        return StreamingResponse(
            doc_buffer,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating multi-product brief: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate multi-product brief")