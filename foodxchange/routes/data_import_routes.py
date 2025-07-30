"""
Data Import Routes for bulk CSV/Excel uploads
"""

from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from typing import Optional
import os
import json
import logging
from pathlib import Path
import io
import pandas as pd

from foodxchange.services.data_import_service import data_import_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import", tags=["Data Import"])

@router.get("/", response_class=HTMLResponse)
async def import_page(request: Request):
    """Data Import page"""
    from foodxchange.main import templates
    return templates.TemplateResponse("pages/data_import.html", {"request": request})

@router.post("/preview")
async def preview_import(
    file: UploadFile = File(...),
    data_type: str = Form(...)
):
    """Preview data before importing"""
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in data_import_service.supported_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported formats: {', '.join(data_import_service.supported_formats)}"
            )
        
        # Save uploaded file temporarily
        temp_dir = os.path.join(os.getcwd(), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_path = os.path.join(temp_dir, file.filename)
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Preview the data
            result = data_import_service.preview_import(temp_path, data_type, limit=20)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error previewing import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process")
async def process_import(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    column_mapping: Optional[str] = Form(None)
):
    """Process the actual import"""
    try:
        # Parse column mapping if provided
        mapping = None
        if column_mapping:
            mapping = json.loads(column_mapping)
        
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in data_import_service.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(data_import_service.supported_formats)}"
            )
        
        # Save uploaded file temporarily
        temp_dir = os.path.join(os.getcwd(), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_path = os.path.join(temp_dir, file.filename)
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Import the data
            result = data_import_service.import_data(temp_path, data_type, mapping)
            
            # If successful, load the imported data
            if result['success']:
                # Read the saved JSON file
                with open(result['file_path'], 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                
                # Add to existing data if any
                data_dir = os.path.join(os.getcwd(), 'data', data_type)
                main_file = os.path.join(data_dir, f'{data_type}.json')
                
                existing_data = []
                if os.path.exists(main_file):
                    with open(main_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                
                # Merge data
                all_data = existing_data + imported_data
                
                # Save merged data
                with open(main_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)
                
                result['total_count'] = len(all_data)
            
            return result
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error processing import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template/{data_type}")
async def download_template(data_type: str):
    """Download a template file for import"""
    try:
        if data_type not in ['buyers', 'suppliers']:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # Generate template
        df = data_import_service.get_import_template(data_type)
        
        # Convert to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=data_type.capitalize())
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={data_type}_import_template.xlsx"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def import_history():
    """Get import history"""
    try:
        history = []
        
        # Check for import files in data directories
        for data_type in ['buyers', 'suppliers']:
            data_dir = os.path.join(os.getcwd(), 'data', data_type)
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.startswith(f'{data_type}_') and filename.endswith('.json'):
                        file_path = os.path.join(data_dir, filename)
                        file_stat = os.stat(file_path)
                        
                        # Get record count
                        with open(file_path, 'r', encoding='utf-8') as f:
                            records = json.load(f)
                        
                        history.append({
                            'filename': filename,
                            'data_type': data_type,
                            'record_count': len(records),
                            'file_size': file_stat.st_size,
                            'import_date': file_stat.st_mtime,
                            'file_path': file_path
                        })
        
        # Sort by import date (newest first)
        history.sort(key=lambda x: x['import_date'], reverse=True)
        
        return {
            'success': True,
            'history': history[:20]  # Limit to last 20 imports
        }
        
    except Exception as e:
        logger.error(f"Error getting import history: {e}")
        return {
            'success': False,
            'error': str(e)
        }