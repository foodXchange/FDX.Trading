# Config module initialization
from .settings import Settings, get_settings, is_production, is_development, get_database_url
from .branding import (
    COMPANY, CONTACT, SOCIAL_MEDIA, STATS, SEO, 
    TRUST_BADGES, PRICING, KEY_FEATURES, NEWSLETTER,
    FOOTER_SECTIONS, CTA_MESSAGES, USER_BENEFITS
)

__all__ = [
    # Settings
    'Settings', 'get_settings', 'is_production', 'is_development', 'get_database_url',
    # Branding
    'COMPANY', 'CONTACT', 'SOCIAL_MEDIA', 'STATS', 'SEO',
    'TRUST_BADGES', 'PRICING', 'KEY_FEATURES', 'NEWSLETTER',
    'FOOTER_SECTIONS', 'CTA_MESSAGES', 'USER_BENEFITS'
]