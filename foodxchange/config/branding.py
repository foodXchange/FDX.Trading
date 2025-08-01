"""
FDX Trading Branding Configuration
Central configuration for all branding elements
"""

# Company Information
COMPANY = {
    "name": "FDX Trading",
    "legal_name": "FDX Trading Ltd.",
    "domain": "fdx.trading",
    "tagline": "AI-Powered Global Food Sourcing Platform",
    "description": "The Operating System for Global Food Trade",
    "founded": "2024",
    "logo_text": {
        "primary": "FDX",
        "secondary": ".TRADING"
    }
}

# Contact Information
CONTACT = {
    "email": "info@fdx.trading",
    "support_email": "support@fdx.trading",
    "sales_email": "sales@fdx.trading",
    "phone": "+972-52-5222291",
    "whatsapp": "+972525222291",
    "address": "Tel Aviv, Israel",
    "office_hours": "Sunday-Thursday, 9:00 AM - 6:00 PM IST"
}

# Social Media Links
SOCIAL_MEDIA = {
    "linkedin": "https://linkedin.com/company/fdx-trading",
    "facebook": "https://facebook.com/fdxtrading",
    "twitter": "https://x.com/fdx_trading",
    "instagram": "https://instagram.com/fdx.trading",
    "youtube": "https://youtube.com/@fdxtrading",
    "whatsapp_business": "https://wa.me/972525222291"
}

# Platform Statistics
STATS = {
    "suppliers": "500+",
    "countries": "50+",
    "products_analyzed": "10,000+",
    "monthly_savings": "$2M+",
    "response_time": "< 2 hours",
    "success_rate": "95%",
    "active_buyers": "10,000+",
    "ai_accuracy": "98%"
}

# SEO & Meta Information
SEO = {
    "title_suffix": " | FDX Trading - AI Food Sourcing",
    "meta_description": "Source food products 10x faster with AI. Connect with 500+ verified suppliers from 50+ countries. Save 15-30% on costs. Start free trial.",
    "keywords": "food sourcing, B2B food trade, AI supplier matching, global food suppliers, food import export, wholesale food platform",
    "og_image": "/static/images/fdx-og-image.png"
}

# Trust Badges & Certifications
TRUST_BADGES = [
    {"name": "SSL Secured", "icon": "fas fa-shield-alt", "color": "success"},
    {"name": "ISO 27001", "icon": "fas fa-check-circle", "color": "info"},
    {"name": "GDPR Compliant", "icon": "fas fa-user-shield", "color": "primary"},
    {"name": "PCI DSS", "icon": "fas fa-credit-card", "color": "warning"}
]

# Pricing Configuration
PRICING = {
    "currency": "$",
    "plans": {
        "trial": {
            "name": "Free Trial",
            "price": 0,
            "period": "14 days",
            "highlights": ["Full access", "No credit card required"]
        },
        "professional": {
            "name": "Professional",
            "price": 299,
            "period": "month",
            "highlights": ["ROI in first month", "Save $5,000+/month average"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": "Custom",
            "period": "",
            "highlights": ["Custom features", "Dedicated support"]
        }
    }
}

# Feature Highlights
KEY_FEATURES = [
    {
        "icon": "🤖",
        "title": "AI-Powered Analysis",
        "description": "Upload product image, get instant supplier matches"
    },
    {
        "icon": "🌍",
        "title": "Global Network",
        "description": "500+ verified suppliers from 50+ countries"
    },
    {
        "icon": "💰",
        "title": "Cost Savings",
        "description": "Save 15-30% on sourcing costs"
    },
    {
        "icon": "⚡",
        "title": "Instant Matching",
        "description": "Get supplier quotes in under 2 hours"
    },
    {
        "icon": "🔒",
        "title": "Secure Transactions",
        "description": "Escrow protection & quality guarantees"
    },
    {
        "icon": "📊",
        "title": "Data Insights",
        "description": "Market analytics & price trends"
    }
]

# Newsletter Configuration
NEWSLETTER = {
    "title": "Get Weekly Sourcing Insights",
    "description": "Join 5,000+ food industry professionals",
    "benefits": [
        "Market price trends",
        "New supplier alerts",
        "Industry best practices",
        "Exclusive platform features"
    ]
}

# Footer Quick Links
FOOTER_SECTIONS = {
    "platform": {
        "title": "Platform",
        "links": [
            {"name": "Features", "url": "/features"},
            {"name": "Pricing", "url": "/pricing"},
            {"name": "Security", "url": "/security"},
            {"name": "API Docs", "url": "/api"}
        ]
    },
    "solutions": {
        "title": "Solutions",
        "links": [
            {"name": "For Buyers", "url": "/for-buyers"},
            {"name": "For Suppliers", "url": "/for-suppliers"},
            {"name": "For Brokers", "url": "/for-brokers"},
            {"name": "Enterprise", "url": "/enterprise"}
        ]
    },
    "resources": {
        "title": "Resources",
        "links": [
            {"name": "Blog", "url": "/blog"},
            {"name": "Case Studies", "url": "/case-studies"},
            {"name": "Help Center", "url": "/help"},
            {"name": "Webinars", "url": "/webinars"}
        ]
    },
    "company": {
        "title": "Company",
        "links": [
            {"name": "About Us", "url": "/about"},
            {"name": "Careers", "url": "/careers"},
            {"name": "Contact", "url": "/contact"},
            {"name": "Press", "url": "/press"}
        ]
    }
}

# Call-to-Action Messages
CTA_MESSAGES = {
    "hero": "Start Sourcing Smarter Today",
    "footer": "Ready to Transform Your Food Sourcing?",
    "pricing": "Get Your ROI in the First Month",
    "demo": "See FDX in Action - Book a Demo",
    "trial": "Start Your 14-Day Free Trial",
    "supplier": "List Your Products for Free"
}

# Platform Benefits by User Type
USER_BENEFITS = {
    "buyers": {
        "title": "For Buyers",
        "subtitle": "Source Products 10x Faster",
        "benefits": [
            "Save 15-30% on sourcing costs",
            "Get quotes in under 2 hours",
            "Access 500+ verified suppliers",
            "AI-powered product matching",
            "Quality guarantees & escrow protection"
        ]
    },
    "suppliers": {
        "title": "For Suppliers",
        "subtitle": "Reach Global Buyers Instantly",
        "benefits": [
            "10,000+ active buyers daily",
            "Zero marketing costs",
            "Automated lead generation",
            "Export to 100+ countries",
            "Guaranteed payment protection"
        ]
    }
}