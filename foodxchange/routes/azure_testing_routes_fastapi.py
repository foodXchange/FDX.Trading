"""
Azure Testing Routes for FastAPI - Real Azure Services Testing and Monitoring
"""

from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from typing import Optional
import os
import asyncio
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
import io

from foodxchange.services.azure_testing_service import azure_testing_service
from foodxchange.services.usage_analytics_service import create_analytics_service
from foodxchange.services.cost_monitoring_service import create_monitoring_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/azure-test", tags=["azure-testing"])

# Test file upload settings
TEST_UPLOAD_FOLDER = 'test_uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'csv', 'xlsx'}

# Create service instances
analytics_service = create_analytics_service(azure_testing_service)
monitoring_service = create_monitoring_service(azure_testing_service)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.get("/")
async def testing_dashboard(request: Request):
    """Azure testing dashboard"""
    from foodxchange.main import templates
    return templates.TemplateResponse("pages/azure_testing.html", {"request": request})

@router.get("/api/status")
async def get_service_status():
    """Get current Azure services status and limits"""
    try:
        # Check service configuration
        services_config = {
            'openai': bool(os.getenv('AZURE_OPENAI_ENDPOINT') and os.getenv('AZURE_OPENAI_API_KEY')),
            'document_intelligence': bool(os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')),
            'translator': bool(os.getenv('AZURE_TRANSLATOR_KEY')),
            'computer_vision': bool(os.getenv('AZURE_VISION_ENDPOINT'))
        }
        
        # Get current limits status
        limits_status = azure_testing_service.get_current_limits_status()
        
        # Get usage summary
        usage_summary = azure_testing_service.get_usage_summary(days=30)
        
        # Check for alerts
        alerts = monitoring_service.check_alerts()
        
        return JSONResponse({
            'success': True,
            'services_configured': services_config,
            'limits_status': limits_status,
            'usage_summary': usage_summary,
            'active_alerts': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/test/product-image")
async def test_product_image(file: UploadFile = File(...)):
    """Test product image analysis with GPT-4 Vision"""
    try:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="Invalid file type")
            
        # Save file temporarily
        os.makedirs(TEST_UPLOAD_FOLDER, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"test_{timestamp}_{file.filename}"
        temp_path = os.path.join(TEST_UPLOAD_FOLDER, temp_filename)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        try:
            # Run analysis
            result = await azure_testing_service.test_product_image_analysis(temp_path)
            
            # Add file info
            result['file_info'] = {
                'name': file.filename,
                'size': len(content),
                'type': file.filename.rsplit('.', 1)[1].lower()
            }
            
            return JSONResponse(result)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error in product image test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/test/csv-translation")
async def test_csv_translation(
    file: UploadFile = File(...),
    source_lang: str = Form('he'),
    target_lang: str = Form('en')
):
    """Test CSV translation"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
            
        # Save file temporarily
        os.makedirs(TEST_UPLOAD_FOLDER, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"test_{timestamp}_{file.filename}"
        temp_path = os.path.join(TEST_UPLOAD_FOLDER, temp_filename)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        try:
            # Run translation
            result = await azure_testing_service.test_csv_translation(
                temp_path, source_lang, target_lang
            )
            
            if result['success']:
                # Convert dataframes to JSON for response
                result['preview'] = {
                    'original': result['original_df'].head(10).to_dict('records'),
                    'translated': result['translated_df'].head(10).to_dict('records')
                }
                # Remove full dataframes from response
                del result['original_df']
                del result['translated_df']
                
                result['file_info'] = {
                    'name': file.filename,
                    'size': len(content),
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
                
            return JSONResponse(result)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error in CSV translation test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/test/document-analysis")
async def test_document_analysis(file: UploadFile = File(...)):
    """Test document analysis with Azure Document Intelligence"""
    try:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="Invalid file type")
            
        # Save file temporarily
        os.makedirs(TEST_UPLOAD_FOLDER, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"test_{timestamp}_{file.filename}"
        temp_path = os.path.join(TEST_UPLOAD_FOLDER, temp_filename)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        try:
            # Run analysis
            result = await azure_testing_service.test_document_analysis(temp_path)
            
            # Add file info
            result['file_info'] = {
                'name': file.filename,
                'size': len(content),
                'type': file.filename.rsplit('.', 1)[1].lower()
            }
            
            return JSONResponse(result)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error in document analysis test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/usage/summary")
async def get_usage_summary(days: int = 30):
    """Get usage summary for specified period"""
    try:
        summary = azure_testing_service.get_usage_summary(days=days)
        
        return JSONResponse({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting usage summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/usage/history")
async def get_usage_history(days: int = 7, service: Optional[str] = None):
    """Get detailed usage history"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        history = azure_testing_service.usage_history
        
        # Filter by date
        filtered = [h for h in history if h.timestamp > cutoff_date]
        
        # Filter by service if specified
        if service:
            filtered = [h for h in filtered if h.service == service]
            
        # Convert to dict for JSON
        history_data = [
            {
                'service': h.service,
                'operation': h.operation,
                'timestamp': h.timestamp.isoformat(),
                'tokens_used': h.tokens_used,
                'characters_processed': h.characters_processed,
                'api_calls': h.api_calls,
                'estimated_cost': h.estimated_cost,
                'success': h.success,
                'error_message': h.error_message,
                'processing_time': h.processing_time
            }
            for h in filtered
        ]
        
        return JSONResponse({
            'success': True,
            'history': history_data,
            'count': len(history_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting usage history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/usage/export")
async def export_usage_data(days: int = 30):
    """Export usage data as CSV"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Prepare data for export
        history = azure_testing_service.usage_history
        filtered = [h for h in history if h.timestamp > cutoff_date]
        
        # Create CSV
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Timestamp', 'Service', 'Operation', 'Success', 
            'Tokens Used', 'Characters Processed', 'API Calls',
            'Estimated Cost ($)', 'Processing Time (s)', 'Error Message'
        ])
        
        # Write data
        for h in filtered:
            writer.writerow([
                h.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                h.service,
                h.operation,
                'Yes' if h.success else 'No',
                h.tokens_used or 0,
                h.characters_processed or 0,
                h.api_calls or 0,
                f"{h.estimated_cost:.4f}",
                f"{h.processing_time:.2f}",
                h.error_message or ''
            ])
            
        # Convert to bytes
        output.seek(0)
        
        filename = f"azure_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting usage data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/test-scenarios")
async def get_test_scenarios():
    """Get predefined test scenarios"""
    scenarios = [
        {
            'id': 'product_hebrew',
            'name': 'Hebrew Product Label',
            'description': 'Test OCR and translation of Hebrew product labels',
            'service': 'openai',
            'sample_file': 'hebrew_product.jpg',
            'estimated_cost': 0.03
        },
        {
            'id': 'supplier_csv',
            'name': 'Multilingual Supplier CSV',
            'description': 'Test translation of supplier data from Hebrew to English',
            'service': 'translator',
            'sample_file': 'suppliers_hebrew.csv',
            'estimated_cost': 0.02
        },
        {
            'id': 'invoice_pdf',
            'name': 'Invoice Analysis',
            'description': 'Extract structured data from PDF invoices',
            'service': 'document_intelligence',
            'sample_file': 'invoice_sample.pdf',
            'estimated_cost': 0.002
        },
        {
            'id': 'catalog_images',
            'name': 'Product Catalog Images',
            'description': 'Batch analyze product images from catalog',
            'service': 'openai',
            'sample_file': 'catalog_page.jpg',
            'estimated_cost': 0.05
        }
    ]
    
    return JSONResponse({
        'success': True,
        'scenarios': scenarios
    })

@router.get("/api/analytics")
async def get_analytics():
    """Get usage analytics and insights"""
    try:
        analytics = analytics_service.analyze_usage_patterns()
        
        return JSONResponse({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/cost-forecast")
async def get_cost_forecast(days: int = 30):
    """Get cost forecast for the specified period"""
    try:
        forecast = analytics_service.get_cost_forecast(days=days)
        
        return JSONResponse({
            'success': True,
            'forecast': forecast
        })
        
    except Exception as e:
        logger.error(f"Error getting cost forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/optimization-opportunities")
async def get_optimization_opportunities():
    """Get optimization opportunities"""
    try:
        opportunities = analytics_service.get_optimization_opportunities()
        
        return JSONResponse({
            'success': True,
            'opportunities': opportunities
        })
        
    except Exception as e:
        logger.error(f"Error getting optimization opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/alerts")
async def get_alerts():
    """Get cost monitoring alerts"""
    try:
        alert_summary = monitoring_service.get_alert_summary()
        
        return JSONResponse({
            'success': True,
            'alerts': alert_summary
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/alerts")
async def create_alert(request: Request):
    """Create a new cost alert"""
    try:
        data = await request.json()
        
        from foodxchange.services.cost_monitoring_service import CostAlert, AlertType
        
        alert = CostAlert(
            id=data['id'],
            name=data['name'],
            type=AlertType(data['type']),
            threshold=float(data['threshold']),
            period=data['period'],
            services=data.get('services', ['all']),
            enabled=data.get('enabled', True),
            notification_email=data.get('notification_email'),
            notification_webhook=data.get('notification_webhook')
        )
        
        if monitoring_service.add_alert(alert):
            return JSONResponse({
                'success': True,
                'message': 'Alert created successfully'
            })
        else:
            raise HTTPException(status_code=400, detail="Alert with this ID already exists")
            
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/alerts/{alert_id}")
async def update_alert(alert_id: str, request: Request):
    """Update an existing alert"""
    try:
        updates = await request.json()
        
        if monitoring_service.update_alert(alert_id, updates):
            return JSONResponse({
                'success': True,
                'message': 'Alert updated successfully'
            })
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
            
    except Exception as e:
        logger.error(f"Error updating alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    try:
        if monitoring_service.delete_alert(alert_id):
            return JSONResponse({
                'success': True,
                'message': 'Alert deleted successfully'
            })
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
            
    except Exception as e:
        logger.error(f"Error deleting alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))