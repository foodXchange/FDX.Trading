"""
Simple Event System for FoodXchange
Just what you need, nothing more
"""

from typing import Dict, List, Callable, Any
from datetime import datetime

# Simple event types - just strings
class Events:
    # When things happen
    SUPPLIER_ADDED = "supplier_added"
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    RESPONSE_RECEIVED = "response_received"
    TASK_CREATED = "task_created"

class SimpleEventBus:
    """Dead simple event bus"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def on(self, event_type: str, handler: Callable):
        """Listen for an event"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def emit(self, event_type: str, data: Any = None):
        """Fire an event"""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Event error: {e}")

# One global instance
bus = SimpleEventBus()

# Super simple usage:
"""
# When email is sent:
bus.emit(Events.EMAIL_SENT, {'supplier_id': 123, 'email': 'test@example.com'})

# Listen for emails:
def log_email(data):
    print(f"Email sent to {data['email']}")
    
bus.on(Events.EMAIL_SENT, log_email)
"""