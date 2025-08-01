"""
Enhanced AI Import Routes with Azure Integration - FastAPI Version
Handles intelligent file analysis and processing
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import json
import asyncio
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

from foodxchange.services.ai_data_import_service import ai_data_import_service
from foodxchange.services.data_import_service import data_import_service

logger = logging.getLogger(__name__)

# Create FastAPI router
ai_import_router = APIRouter(prefix="/api/import", tags=["AI Import"])

# Configure upload settings
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def validate_file_size(file: UploadFile) -> bool:
    """Validate file size"""
    # Read file content to check size
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    return len(content) <= MAX_FILE_SIZE

@ai_import_router.post("/analyze-ai")
async def analyze_file_with_ai(
    file: UploadFile = File(...),
    data_type: str = Form("suppliers")
):
    """
    Analyze uploaded file with AI for intelligent field mapping
    
    Expected form data:
    - file: The uploaded CSV/Excel file
    - data_type: Type of data (suppliers, buyers, products)
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Allowed: CSV, XLSX, XLS"
            )
        
        if not await validate_file_size(file):
            raise HTTPException(
                status_code=400, 
                detail="File too large. Maximum size: 10MB"
            )
        
        # Create upload directory if needed
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file temporarily
        filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"{timestamp}_{filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        # Save uploaded file
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        try:
            # Analyze with AI
            analysis_result = await ai_data_import_service.analyze_import_file(
                file_data=content,
                file_name=filename,
                entity_type=data_type
            )
            
            if analysis_result['success']:
                # Store temp file path for later processing
                analysis_result['data']['file_path'] = temp_path
                analysis_result['data']['original_filename'] = filename
                
                # Add statistics
                sample_data = analysis_result.get('sample_data', {})
                if sample_data:
                    analysis_result['data']['stats'] = {
                        'total_rows': sample_data.get('stats', {}).get('total_rows', 0),
                        'total_columns': sample_data.get('stats', {}).get('total_columns', 0),
                        'file_size': os.path.getsize(temp_path),
                        'file_type': filename.rsplit('.', 1)[1].lower()
                    }
                
                return analysis_result
            else:
                # Clean up on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise HTTPException(status_code=400, detail=analysis_result.get('error', 'Analysis failed'))
                
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

@ai_import_router.post("/process-ai")
async def process_import_with_ai(request: Request):
    """
    Process import with AI assistance using confirmed mappings
    
    Expected JSON data:
    - file_path: Path to the temporary file
    - data_type: Type of data being imported
    - analysis: AI analysis results
    - user_confirmations: User-confirmed field mappings
    """
    try:
        data = await request.json()
        
        if not data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        file_path = data.get('file_path')
        data_type = data.get('data_type')
        analysis = data.get('analysis')
        user_confirmations = data.get('user_confirmations', {})
        
        # Validate required fields
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="File not found")
        
        if not data_type:
            raise HTTPException(status_code=400, detail="Data type not specified")
        
        if not analysis:
            raise HTTPException(status_code=400, detail="Analysis data not provided")
        
        try:
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Apply mappings and clean data
            result = await ai_data_import_service.apply_mappings_and_clean(
                file_data=file_data,
                file_name=os.path.basename(file_path),
                mappings=analysis,
                user_confirmations=user_confirmations
            )
            
            if result['success']:
                # Add import metadata
                result['data']['import_metadata'] = {
                    'imported_at': datetime.now().isoformat(),
                    'data_type': data_type,
                    'ai_assisted': True,
                    'original_filename': analysis.get('original_filename', 'unknown'),
                    'mapping_coverage': analysis.get('mapping_coverage', 0)
                }
                
                return {
                    'success': True,
                    'data': result['data'],
                    'message': 'Data processed successfully'
                }
            else:
                raise HTTPException(status_code=400, detail=result.get('error', 'Processing failed'))
                
        finally:
            # Always clean up temp file after processing
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing import: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Processing failed: {str(e)}"
        )

@ai_import_router.post("/finalize")
async def finalize_import(request: Request):
    """
    Finalize the import and save data to database
    
    Expected JSON data:
    - cleaned_data: The cleaned and validated data
    - data_type: Type of data being imported
    - import_metadata: Metadata about the import
    """
    try:
        data = await request.json()
        
        cleaned_data = data.get('cleaned_data', [])
        data_type = data.get('data_type')
        import_metadata = data.get('import_metadata', {})
        
        if not cleaned_data:
            raise HTTPException(status_code=400, detail="No data to import")
        
        # Add timestamps
        timestamp = datetime.now().isoformat()
        for record in cleaned_data:
            record['created_at'] = timestamp
            record['updated_at'] = timestamp
            record['imported_via'] = 'ai_assisted'
            record['import_batch_id'] = import_metadata.get('batch_id', timestamp)
        
        # Save to database/file
        output_dir = Path('data') / data_type
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f'{data_type}_ai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        # Merge with existing data
        main_file = output_dir / f'{data_type}.json'
        existing_data = []
        
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # Add new data
        all_data = existing_data + cleaned_data
        
        # Save merged data
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'imported_count': len(cleaned_data),
            'total_count': len(all_data),
            'message': f'Successfully imported {len(cleaned_data)} {data_type}',
            'import_file': str(output_file)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finalizing import: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Import failed: {str(e)}"
        )

@ai_import_router.post("/validate-mapping")
async def validate_mapping(request: Request):
    """
    Validate a specific field mapping suggestion
    
    Expected JSON data:
    - source_field: The source field name
    - target_field: The target field name
    - sample_values: Sample values from the source field
    """
    try:
        data = await request.json()
        
        source_field = data.get('source_field')
        target_field = data.get('target_field')
        sample_values = data.get('sample_values', [])
        
        # Perform validation logic
        validation_result = {
            'valid': True,
            'confidence': 0.95,
            'issues': [],
            'suggestions': []
        }
        
        # Check for common issues
        if target_field == 'email' and sample_values:
            invalid_emails = [v for v in sample_values if '@' not in str(v)]
            if invalid_emails:
                validation_result['valid'] = False
                validation_result['confidence'] = 0.3
                validation_result['issues'].append(f"Found {len(invalid_emails)} invalid email formats")
                validation_result['suggestions'].append("Consider data cleaning or manual review")
        
        elif target_field == 'phone' and sample_values:
            # Basic phone validation
            invalid_phones = [v for v in sample_values if len(str(v).strip()) < 6]
            if invalid_phones:
                validation_result['confidence'] = 0.7
                validation_result['suggestions'].append("Some phone numbers may need formatting")
        
        return {
            'success': True,
            'validation': validation_result
        }
        
    except Exception as e:
        logger.error(f"Error validating mapping: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Validation failed: {str(e)}"
        )

@ai_import_router.get("/ai-status")
async def check_ai_status():
    """Check if AI features are properly configured"""
    try:
        status = {
            'openai_configured': bool(os.getenv('AZURE_OPENAI_ENDPOINT') and os.getenv('AZURE_OPENAI_API_KEY')),
            'document_intelligence_configured': bool(os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')),
            'translator_configured': bool(os.getenv('AZURE_TRANSLATOR_KEY')),
            'vision_configured': bool(os.getenv('AZURE_VISION_ENDPOINT')),
            'gpt4_available': os.getenv('AZURE_OPENAI_VISION_DEPLOYMENT') == 'gpt-4o'
        }
        
        all_configured = all(status.values())
        
        return {
            'success': True,
            'ai_enabled': all_configured,
            'services': status,
            'message': 'All AI services configured' if all_configured else 'Some AI services not configured'
        }
        
    except Exception as e:
        logger.error(f"Error checking AI status: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        ) 