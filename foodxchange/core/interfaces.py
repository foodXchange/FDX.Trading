"""
Core interfaces for dependency injection and abstraction
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar('T')


class CacheProvider(ABC):
    """Abstract cache provider interface"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in cache with TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        pass
    
    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern"""
        pass


class AIClient(ABC):
    """Abstract AI client interface"""
    
    @abstractmethod
    async def analyze_product(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """Analyze product from image data"""
        pass
    
    @abstractmethod
    async def extract_text(self, image_data: bytes) -> str:
        """Extract text from image"""
        pass


class DatabaseProvider(ABC):
    """Abstract database provider interface"""
    
    @abstractmethod
    async def get_session(self):
        """Get database session"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute raw query"""
        pass


class FileStorageProvider(ABC):
    """Abstract file storage interface"""
    
    @abstractmethod
    async def save_file(self, file_data: bytes, filename: str, folder: str = "") -> str:
        """Save file and return path/URL"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        pass


class NotificationProvider(ABC):
    """Abstract notification provider interface"""
    
    @abstractmethod
    async def send_email(self, to: str, subject: str, content: str) -> bool:
        """Send email notification"""
        pass
    
    @abstractmethod
    async def send_push_notification(self, user_id: str, message: str) -> bool:
        """Send push notification"""
        pass