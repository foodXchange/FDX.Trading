"""
Azure Testing Routes - Real Azure Services Testing and Monitoring
"""

from flask import Blueprint, request, jsonify, render_template, current_app, send_file
import os
import asyncio
from datetime import datetime, timedelta
import json
from werkzeug.utils import secure_filename
import logging

from foodxchange.services.azure_testing_service import azure_testing_service

logger = logging.getLogger(__name__)

# Create blueprint
azure_testing_bp = Blueprint('azure_testing', __name__, url_prefix='/azure-test')

# Test file upload settings
TEST_UPLOAD_FOLDER = 'test_uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@azure_testing_bp.route('/')
def testing_dashboard():
    """Azure testing dashboard"""
    return render_template('pages/azure_testing.html')

@azure_testing_bp.route('/api/status')
def get_service_status():
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
        
        return jsonify({
            'success': True,
            'services_configured': services_config,
            'limits_status': limits_status,
            'usage_summary': usage_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@azure_testing_bp.route('/api/test/product-image', methods=['POST'])
async def test_product_image():
    """Test product image analysis with GPT-4 Vision"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
            
        # Save file temporarily
        os.makedirs(TEST_UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"test_{timestamp}_{filename}"
        temp_path = os.path.join(TEST_UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
        try:
            # Run analysis
            result = await azure_testing_service.test_product_image_analysis(temp_path)
            
            # Add file info
            result['file_info'] = {
                'name': filename,
                'size': os.path.getsize(temp_path),
                'type': filename.rsplit('.', 1)[1].lower()
            }
            
            return jsonify(result)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error in product image test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@azure_testing_bp.route('/api/test/csv-translation', methods=['POST'])
async def test_csv_translation():
    """Test CSV translation"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
            
        file = request.files['file']
        source_lang = request.form.get('source_lang', 'he')
        target_lang = request.form.get('target_lang', 'en')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'Only CSV files are supported'}), 400
            
        # Save file temporarily
        os.makedirs(TEST_UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"test_{timestamp}_{filename}"
        temp_path = os.path.join(TEST_UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
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
                    'name': filename,
                    'size': os.path.getsize(temp_path),
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
                
            return jsonify(result)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error in CSV translation test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@azure_testing_bp.route('/api/test/document-analysis', methods=['POST'])
async def test_document_analysis():
    """Test document analysis with Azure Document Intelligence"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
            
        # Save file temporarily
        os.makedirs(TEST_UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"test_{timestamp}_{filename}"
        temp_path = os.path.join(TEST_UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
        try:
            # Run analysis
            result = await azure_testing_service.test_document_analysis(temp_path)
            
            # Add file info
            result['file_info'] = {
                'name': filename,
                'size': os.path.getsize(temp_path),
                'type': filename.rsplit('.', 1)[1].lower()
            }
            
            return jsonify(result)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error in document analysis test: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@azure_testing_bp.route('/api/usage/summary')
def get_usage_summary():
    """Get usage summary for specified period"""
    try:
        days = request.args.get('days', 30, type=int)
        summary = azure_testing_service.get_usage_summary(days=days)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting usage summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@azure_testing_bp.route('/api/usage/history')
def get_usage_history():
    """Get detailed usage history"""
    try:
        days = request.args.get('days', 7, type=int)
        service = request.args.get('service', None)
        
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
        
        return jsonify({
            'success': True,
            'history': history_data,
            'count': len(history_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting usage history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@azure_testing_bp.route('/api/usage/export')
def export_usage_data():
    """Export usage data as CSV"""
    try:
        days = request.args.get('days', 30, type=int)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Prepare data for export
        history = azure_testing_service.usage_history
        filtered = [h for h in history if h.timestamp > cutoff_date]
        
        # Create CSV
        import csv
        from io import StringIO, BytesIO
        
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
        data = BytesIO()
        data.write(output.getvalue().encode('utf-8'))
        data.seek(0)
        
        filename = f"azure_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error exporting usage data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@azure_testing_bp.route('/api/test-scenarios')
def get_test_scenarios():
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
    
    return jsonify({
        'success': True,
        'scenarios': scenarios
    })

# Error handlers
@azure_testing_bp.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB'
    }), 413

@azure_testing_bp.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled exception in Azure testing: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'An unexpected error occurred'
    }), 500