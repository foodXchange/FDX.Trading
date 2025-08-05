"""
Lean Email Tracker for FoodXchange
Simple open/click tracking that actually works
"""

import uuid
from datetime import datetime
from typing import Optional
import psycopg2
from app.core.events import bus, Events

class EmailTracker:
    """Simple email tracking - opens and clicks"""
    
    def __init__(self, db_url: str, app_url: str = "https://fdx.trading"):
        self.db_url = db_url
        self.app_url = app_url
    
    def create_tracking_id(self) -> str:
        """Generate unique tracking ID"""
        return str(uuid.uuid4())[:8]  # Short ID
    
    def add_tracking(self, email_content: str, tracking_id: str) -> str:
        """Add tracking pixel and wrap links"""
        
        # Add invisible tracking pixel at end
        pixel = f'<img src="{self.app_url}/t/{tracking_id}.gif" width="1" height="1" />'
        
        # Simple link wrapping - just wrap email addresses for now
        tracked_content = email_content.replace(
            'partnerships@fdx.trading',
            f'<a href="{self.app_url}/c/{tracking_id}?u=mailto:partnerships@fdx.trading">partnerships@fdx.trading</a>'
        )
        
        # Add pixel to HTML emails
        if '<html>' in tracked_content.lower():
            tracked_content = tracked_content.replace('</body>', f'{pixel}</body>')
        else:
            # Convert plain text to simple HTML
            tracked_content = f"""<html><body>
{tracked_content.replace(chr(10), '<br>')}
{pixel}
</body></html>"""
        
        return tracked_content
    
    def track_open(self, tracking_id: str):
        """Record email open"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Update open time
            cur.execute("""
                UPDATE email_log 
                SET opened_at = COALESCE(opened_at, NOW()),
                    open_count = COALESCE(open_count, 0) + 1
                WHERE tracking_id = %s
            """, (tracking_id,))
            
            # Get supplier info for event
            cur.execute("""
                SELECT supplier_id, supplier_email 
                FROM email_log 
                WHERE tracking_id = %s
            """, (tracking_id,))
            
            result = cur.fetchone()
            if result:
                bus.emit(Events.EMAIL_OPENED, {
                    'tracking_id': tracking_id,
                    'supplier_id': result[0],
                    'email': result[1]
                })
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Track open error: {e}")
    
    def track_click(self, tracking_id: str, url: str):
        """Record link click"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Update click time
            cur.execute("""
                UPDATE email_log 
                SET clicked_at = COALESCE(clicked_at, NOW()),
                    click_count = COALESCE(click_count, 0) + 1
                WHERE tracking_id = %s
            """, (tracking_id,))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Track click error: {e}")
    
    def get_pixel_image(self) -> bytes:
        """Return 1x1 transparent GIF"""
        # Smallest possible transparent GIF
        return bytes.fromhex('47494638396101000100800000000000ffffff00000021f90401000000002c00000000010001000002024401003b')