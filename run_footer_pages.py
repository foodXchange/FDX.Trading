#!/usr/bin/env python3
"""
Simple Flask server for FDX footer pages
Runs on port 9000
"""

from flask import Flask, render_template, jsonify, request
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create Flask app
app = Flask(__name__, 
            template_folder='foodxchange/templates',
            static_folder='foodxchange/static')

# Configure app
app.config['SECRET_KEY'] = 'fdx-footer-pages-2024'

# Import branding config
try:
    from foodxchange.config.branding import COMPANY, CONTACT, SOCIAL_MEDIA, STATS
    branding_data = {
        'company': COMPANY,
        'contact': CONTACT,
        'social_media': SOCIAL_MEDIA,
        'stats': STATS
    }
except ImportError:
    print("Warning: Could not import branding config")
    branding_data = {}

# Footer page routes
@app.route('/features')
def features():
    return render_template('pages/features.html', **branding_data)

@app.route('/pricing')
def pricing():
    return render_template('pages/pricing.html', **branding_data)

@app.route('/security')
def security():
    return render_template('pages/security.html', **branding_data)

@app.route('/api')
def api():
    return render_template('pages/api.html', **branding_data)

@app.route('/for-buyers')
def for_buyers():
    return render_template('pages/for_buyers.html', **branding_data)

@app.route('/for-suppliers')
def for_suppliers():
    return render_template('pages/for_suppliers.html', **branding_data)

@app.route('/for-brokers')
def for_brokers():
    return render_template('pages/for_brokers.html', **branding_data)

@app.route('/enterprise')
def enterprise():
    return render_template('pages/enterprise.html', **branding_data)

@app.route('/about')
def about():
    return render_template('pages/about.html', **branding_data)

@app.route('/careers')
def careers():
    return render_template('pages/careers.html', **branding_data)

@app.route('/blog')
def blog():
    return render_template('pages/blog.html', **branding_data)

@app.route('/contact')
def contact():
    return render_template('pages/contact.html', **branding_data)

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'FDX Footer Pages',
        'port': 9000
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    # Return JSON response to match the format you're seeing
    return jsonify({
        "success": False,
        "data": None,
        "error": {
            "error_code": "HTTP_404",
            "message": "Page Not Found",
            "details": f"The requested URL {request.path} was not found on the server."
        }
    }), 404

if __name__ == '__main__':
    print("Starting FDX Footer Pages Server...")
    print("Available routes:")
    print("  http://localhost:9000/features")
    print("  http://localhost:9000/pricing")
    print("  http://localhost:9000/security")
    print("  http://localhost:9000/for-buyers")
    print("  http://localhost:9000/for-suppliers")
    print("  http://localhost:9000/about")
    print("  http://localhost:9000/contact")
    print("  http://localhost:9000/blog")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=9000, debug=True)