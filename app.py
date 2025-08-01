"""
FoodXchange (FDX) - AI-Powered B2B Food Trading Platform
Main Flask application following FDX deployment standards
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from config import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    mail = Mail(app)
    csrf = CSRFProtect(app)
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        logger.info(f"{request.method} {request.url}")
    
    # Main routes
    @app.route('/')
    def index():
        """Main homepage with modern interactive elements"""
        try:
            data = {
                'company_name': 'FoodXchange (FDX)',
                'tagline': 'AI-Powered B2B Food Trading Platform',
                'current_year': datetime.now().year,
                'stats': {
                    'time_saved': 70,
                    'cost_reduction': 95,
                    'revenue_saved': 2000000,
                    'faster_sourcing': 70,
                    'error_reduction': 95,
                    'annual_savings': 2000000
                },
                'benefits': {
                    'buyers': [
                        '70% Faster Sourcing: Find verified suppliers in minutes, not months',
                        'Zero Compliance Risk: Automated checks ensure every product meets standards',
                        'Complete Visibility: Track every sample, document, and shipment in real-time',
                        'Smarter Decisions: AI-powered insights help you choose the best suppliers',
                        'Unified Workspace: Replace 10+ tools with one intelligent platform'
                    ],
                    'sellers': [
                        'Global Reach: Connect with verified international buyers instantly',
                        'Win More Deals: AI helps match you with perfect opportunities',
                        'Showcase Excellence: Digital catalog with certifications and capabilities',
                        'Faster Payments: Streamlined processes mean quicker deal closure',
                        'Build Trust: Performance ratings and verified credentials'
                    ]
                },
                'workflow_steps': [
                    {
                        'number': 1,
                        'icon': 'fa-file-alt',
                        'title': 'Submit Smart RFQ',
                        'description': 'AI-assisted request forms capture every requirement perfectly'
                    },
                    {
                        'number': 2,
                        'icon': 'fa-users',
                        'title': 'Receive Matched Offers',
                        'description': 'Verified suppliers automatically matched to your needs'
                    },
                    {
                        'number': 3,
                        'icon': 'fa-balance-scale',
                        'title': 'Compare & Select',
                        'description': 'Side-by-side comparisons with intelligent recommendations'
                    },
                    {
                        'number': 4,
                        'icon': 'fa-vial',
                        'title': 'Track Samples',
                        'description': 'Real-time sample management with automated reminders'
                    },
                    {
                        'number': 5,
                        'icon': 'fa-certificate',
                        'title': 'Ensure Compliance',
                        'description': 'Automated checks for kosher, organic, and regulatory standards'
                    },
                    {
                        'number': 6,
                        'icon': 'fa-handshake',
                        'title': 'Complete Deal',
                        'description': 'Digital contracts and seamless logistics coordination'
                    }
                ],
                'ai_features': [
                    {
                        'icon': 'fa-brain',
                        'title': 'Smart Matching',
                        'description': 'AI analyzes requirements and instantly connects you with the most suitable partners'
                    },
                    {
                        'icon': 'fa-robot',
                        'title': 'Compliance Automation',
                        'description': 'Automatic validation of certifications, labels, and regulatory requirements'
                    },
                    {
                        'icon': 'fa-chart-line',
                        'title': 'Predictive Insights',
                        'description': 'Anticipate delays, price changes, and quality issues before they happen'
                    },
                    {
                        'icon': 'fa-language',
                        'title': 'Multi-Language Support',
                        'description': 'Seamless communication across borders with intelligent translation'
                    }
                ],
                'about_stats': {
                    'years_experience': '20+',
                    'addressable_market': '€30B',
                    'active_partners': '500+',
                    'annual_growth': '15%'
                },
                'transformation': {
                    'before': {
                        'title': 'Before FoodXchange',
                        'points': [
                            '8+ hours creating and sending RFQs',
                            '3-5 days for supplier responses',
                            'Manual compliance verification',
                            'Fragmented communication channels',
                            'Limited supplier visibility'
                        ]
                    },
                    'after': {
                        'title': 'With FoodXchange',
                        'points': [
                            '15 minutes to reach 100+ suppliers',
                            'Real-time responses and comparisons',
                            'Automated compliance tracking',
                            'Centralized communication hub',
                            'Global supplier network access'
                        ]
                    }
                }
            }
            
            return render_template('index.html', **data)
            
        except Exception as e:
            logger.error(f"Homepage error: {e}")
            return render_template('error.html', error="Unable to load homepage"), 500
    
    @app.route('/api/contact', methods=['POST'])
    def contact():
        """Handle contact form submissions"""
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            company = request.form.get('company', '')
            message = request.form.get('message')
            
            if not all([name, email, message]):
                return jsonify({
                    'status': 'error',
                    'message': 'Name, email, and message are required.'
                }), 400
            
            # Send email notification (if configured)
            try:
                msg = Message(
                    subject=f"{app.config['FDX_MAIL_SUBJECT_PREFIX']}New Contact Form Submission",
                    sender=app.config['FDX_MAIL_SENDER'],
                    recipients=[app.config['FDX_ADMIN']],
                    body=f"""
New contact form submission:

Name: {name}
Email: {email}
Company: {company}
Message: {message}

Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                )
                mail.send(msg)
                logger.info(f"Contact form submitted: {email}")
            except Exception as mail_error:
                logger.error(f"Failed to send contact email: {mail_error}")
            
            return jsonify({
                'status': 'success',
                'message': 'Thank you for contacting us. We will get back to you soon.'
            })
            
        except Exception as e:
            logger.error(f"Contact form error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            }), 500
    
    @app.route('/api/demo', methods=['POST'])
    def request_demo():
        """Handle demo request submissions"""
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            company = request.form.get('company')
            phone = request.form.get('phone', '')
            preferred_time = request.form.get('preferred_time', '')
            
            if not all([name, email, company]):
                return jsonify({
                    'status': 'error',
                    'message': 'Name, email, and company are required.'
                }), 400
            
            # Log demo request
            logger.info(f"Demo request: {email} from {company}")
            
            # Send email notification (if configured)
            try:
                msg = Message(
                    subject=f"{app.config['FDX_MAIL_SUBJECT_PREFIX']}New Demo Request",
                    sender=app.config['FDX_MAIL_SENDER'],
                    recipients=[app.config['FDX_ADMIN']],
                    body=f"""
New demo request:

Name: {name}
Email: {email}
Company: {company}
Phone: {phone}
Preferred Time: {preferred_time}

Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                )
                mail.send(msg)
            except Exception as mail_error:
                logger.error(f"Failed to send demo email: {mail_error}")
            
            return jsonify({
                'status': 'success',
                'message': 'Demo request received. Our team will contact you within 24 hours.'
            })
            
        except Exception as e:
            logger.error(f"Demo request error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            }), 500
    
    @app.route('/api/trial', methods=['POST'])
    def start_trial():
        """Handle trial signup submissions"""
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            company = request.form.get('company')
            company_size = request.form.get('company_size')
            country = request.form.get('country')
            
            if not all([name, email, company, company_size, country]):
                return jsonify({
                    'status': 'error',
                    'message': 'All fields are required for trial signup.'
                }), 400
            
            # Log trial request
            logger.info(f"Trial request: {email} from {company} ({country})")
            
            # Send email notification (if configured)
            try:
                msg = Message(
                    subject=f"{app.config['FDX_MAIL_SUBJECT_PREFIX']}New Trial Signup",
                    sender=app.config['FDX_MAIL_SENDER'],
                    recipients=[app.config['FDX_ADMIN']],
                    body=f"""
New trial signup:

Name: {name}
Email: {email}
Company: {company}
Company Size: {company_size}
Country: {country}

Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                )
                mail.send(msg)
            except Exception as mail_error:
                logger.error(f"Failed to send trial email: {mail_error}")
            
            return jsonify({
                'status': 'success',
                'message': 'Your free trial has been activated. Check your email for login details.'
            })
            
        except Exception as e:
            logger.error(f"Trial request error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            }), 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'FDX Trading Platform',
            'version': '1.0.0'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    logger.info("Starting FDX Trading Platform...")
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )