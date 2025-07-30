"""
Enhanced AI Import Routes with Azure Integration
Handles intelligent file analysis and processing
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import asyncio
import pandas as pd
from datetime import datetime
import logging

from foodxchange.services.ai_data_import_service import ai_data_import_service
from foodxchange.services.data_import_service import data_import_service

logger = logging.getLogger(__name__)

# Create blueprint
ai_import_bp = Blueprint('ai_import', __name__, url_prefix='/api/import')

# Configure upload settings
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE

@ai_import_bp.route('/analyze-ai', methods=['POST'])
async def analyze_file_with_ai():
    """
    Analyze uploaded file with AI for intelligent field mapping
    
    Expected form data:
    - file: The uploaded CSV/Excel file
    - data_type: Type of data (suppliers, buyers, products)
    """
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        data_type = request.form.get('data_type', 'suppliers')
        
        # Validate file
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Allowed: CSV, XLSX, XLS'}), 400
        
        if not validate_file_size(file):
            return jsonify({'success': False, 'error': 'File too large. Maximum size: 10MB'}), 400
        
        # Create upload directory if needed
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"{timestamp}_{filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
        try:
            # Read file for analysis
            with open(temp_path, 'rb') as f:
                file_data = f.read()
            
            # Analyze with AI
            analysis_result = await ai_data_import_service.analyze_import_file(
                file_data=file_data,
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
                
                return jsonify(analysis_result)
            else:
                # Clean up on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify(analysis_result), 400
                
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
            
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@ai_import_bp.route('/process-ai', methods=['POST'])
async def process_import_with_ai():
    """
    Process import with AI assistance using confirmed mappings
    
    Expected JSON data:
    - file_path: Path to the temporary file
    - data_type: Type of data being imported
    - analysis: AI analysis results
    - user_confirmations: User-confirmed field mappings
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        file_path = data.get('file_path')
        data_type = data.get('data_type')
        analysis = data.get('analysis')
        user_confirmations = data.get('user_confirmations', {})
        
        # Validate required fields
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 400
        
        if not data_type:
            return jsonify({'success': False, 'error': 'Data type not specified'}), 400
        
        if not analysis:
            return jsonify({'success': False, 'error': 'Analysis data not provided'}), 400
        
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
                
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'message': 'Data processed successfully'
                })
            else:
                return jsonify(result), 400
                
        finally:
            # Always clean up temp file after processing
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        logger.error(f"Error processing import: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500

@ai_import_bp.route('/finalize', methods=['POST'])
async def finalize_import():
    """
    Finalize the import and save data to database
    
    Expected JSON data:
    - cleaned_data: The cleaned and validated data
    - data_type: Type of data being imported
    - import_metadata: Metadata about the import
    """
    try:
        data = request.get_json()
        
        cleaned_data = data.get('cleaned_data', [])
        data_type = data.get('data_type')
        import_metadata = data.get('import_metadata', {})
        
        if not cleaned_data:
            return jsonify({'success': False, 'error': 'No data to import'}), 400
        
        # Add timestamps
        timestamp = datetime.now().isoformat()
        for record in cleaned_data:
            record['created_at'] = timestamp
            record['updated_at'] = timestamp
            record['imported_via'] = 'ai_assisted'
            record['import_batch_id'] = import_metadata.get('batch_id', timestamp)
        
        # Save to database/file
        output_dir = os.path.join(current_app.root_path, '..', 'data', data_type)
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(
            output_dir,
            f'{data_type}_ai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        # Merge with existing data
        main_file = os.path.join(output_dir, f'{data_type}.json')
        existing_data = []
        
        if os.path.exists(main_file):
            with open(main_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # Add new data
        all_data = existing_data + cleaned_data
        
        # Save merged data
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'imported_count': len(cleaned_data),
            'total_count': len(all_data),
            'message': f'Successfully imported {len(cleaned_data)} {data_type}',
            'import_file': output_file
        })
        
    except Exception as e:
        logger.error(f"Error finalizing import: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Import failed: {str(e)}'
        }), 500

@ai_import_bp.route('/validate-mapping', methods=['POST'])
async def validate_mapping():
    """
    Validate a specific field mapping suggestion
    
    Expected JSON data:
    - source_field: The source field name
    - target_field: The target field name
    - sample_values: Sample values from the source field
    """
    try:
        data = request.get_json()
        
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
        
        return jsonify({
            'success': True,
            'validation': validation_result
        })
        
    except Exception as e:
        logger.error(f"Error validating mapping: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}'
        }), 500

@ai_import_bp.route('/ai-status', methods=['GET'])
def check_ai_status():
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
        
        return jsonify({
            'success': True,
            'ai_enabled': all_configured,
            'services': status,
            'message': 'All AI services configured' if all_configured else 'Some AI services not configured'
        })
        
    except Exception as e:
        logger.error(f"Error checking AI status: {str(e)}")
        return jsonify({
            'success': False,
            'ai_enabled': False,
            'error': str(e)
        }), 500

# Error handler for the blueprint
@ai_import_bp.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB'
    }), 413

@ai_import_bp.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled exception in AI import: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'An unexpected error occurred'
    }), 500