"""
Azure Blob Storage Service for FoodXchange
Handles document storage, file uploads, and attachments
"""
import os
import logging
from typing import Optional, List, Dict, BinaryIO
from datetime import datetime, timedelta
import mimetypes
from uuid import uuid4

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    print("Warning: azure-storage-blob package not installed. Run: pip install azure-storage-blob")

from app.config import get_settings

logger = logging.getLogger(__name__)


class BlobStorageService:
    """Service for Azure Blob Storage operations"""
    
    # Container names
    CONTAINERS = {
        "quotes": "quotes",           # PDF quotes from suppliers
        "orders": "orders",           # Order documents
        "products": "products",       # Product images and specs
        "suppliers": "suppliers",     # Supplier certificates, licenses
        "emails": "email-attachments" # Email attachments
    }
    
    # Allowed file extensions by container
    ALLOWED_EXTENSIONS = {
        "quotes": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
        "orders": [".pdf", ".doc", ".docx"],
        "products": [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"],
        "suppliers": [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"],
        "emails": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png", ".zip"]
    }
    
    def __init__(self):
        self.settings = get_settings()
        self.blob_service_client = None
        self.account_name = None
        
        if AZURE_STORAGE_AVAILABLE and self.settings.azure_storage_connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.settings.azure_storage_connection_string
                )
                # Extract account name from connection string
                for part in self.settings.azure_storage_connection_string.split(';'):
                    if part.startswith('AccountName='):
                        self.account_name = part.split('=')[1]
                        break
                
                logger.info("Azure Blob Storage client initialized successfully")
                self._ensure_containers_exist()
            except Exception as e:
                logger.error(f"Failed to initialize Blob Storage: {e}")
                self.blob_service_client = None
        else:
            logger.warning("Azure Blob Storage not configured. Check AZURE_STORAGE_CONNECTION_STRING")
    
    def _ensure_containers_exist(self):
        """Create containers if they don't exist"""
        if not self.blob_service_client:
            return
        
        for container_name in self.CONTAINERS.values():
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client.create_container(public_access="None")
                    logger.info(f"Created container: {container_name}")
            except Exception as e:
                logger.error(f"Error creating container {container_name}: {e}")
    
    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        container_type: str,
        company_id: int,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, str]]:
        """
        Upload a file to blob storage
        
        Args:
            file: File object to upload
            filename: Original filename
            container_type: Type of container (quotes, orders, etc.)
            company_id: Company ID for organization
            metadata: Optional metadata to store with blob
            
        Returns:
            Dict with blob_name and url if successful, None otherwise
        """
        if not self.blob_service_client:
            logger.error("Blob storage not initialized")
            return None
        
        container_name = self.CONTAINERS.get(container_type)
        if not container_name:
            logger.error(f"Invalid container type: {container_type}")
            return None
        
        # Validate file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.ALLOWED_EXTENSIONS.get(container_type, []):
            logger.error(f"File extension {file_ext} not allowed for {container_type}")
            return None
        
        try:
            # Generate unique blob name with folder structure
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid4())[:8]
            safe_filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
            blob_name = f"company_{company_id}/{timestamp}_{unique_id}_{safe_filename}"
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Set content type
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            
            # Prepare metadata
            blob_metadata = {
                "company_id": str(company_id),
                "original_filename": filename,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            if metadata:
                blob_metadata.update(metadata)
            
            # Upload file
            blob_client.upload_blob(
                file,
                content_type=content_type,
                metadata=blob_metadata,
                overwrite=True
            )
            
            logger.info(f"Uploaded file: {blob_name} to {container_name}")
            
            return {
                "blob_name": blob_name,
                "container": container_name,
                "url": self.get_blob_url(container_name, blob_name),
                "sas_url": self.generate_sas_url(container_name, blob_name, hours=24)
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None
    
    def get_blob_url(self, container_name: str, blob_name: str) -> str:
        """Get the public URL for a blob (requires SAS token for access)"""
        if not self.account_name:
            return ""
        return f"https://{self.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    
    def generate_sas_url(
        self,
        container_name: str,
        blob_name: str,
        hours: int = 1,
        permission: str = "r"
    ) -> Optional[str]:
        """
        Generate a SAS URL for temporary access to a blob
        
        Args:
            container_name: Container name
            blob_name: Blob name
            hours: Hours until expiration
            permission: Permissions (r=read, w=write, d=delete)
            
        Returns:
            SAS URL if successful, None otherwise
        """
        if not self.blob_service_client or not self.account_name:
            return None
        
        try:
            # Get account key from connection string
            account_key = None
            for part in self.settings.azure_storage_connection_string.split(';'):
                if part.startswith('AccountKey='):
                    account_key = part.split('=', 1)[1]
                    break
            
            if not account_key:
                logger.error("Account key not found in connection string")
                return None
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=container_name,
                blob_name=blob_name,
                account_key=account_key,
                permission=BlobSasPermissions(read="r" in permission, write="w" in permission, delete="d" in permission),
                expiry=datetime.utcnow() + timedelta(hours=hours)
            )
            
            # Construct URL
            blob_url = self.get_blob_url(container_name, blob_name)
            return f"{blob_url}?{sas_token}"
            
        except Exception as e:
            logger.error(f"Failed to generate SAS URL: {e}")
            return None
    
    async def download_file(self, container_name: str, blob_name: str) -> Optional[bytes]:
        """Download a file from blob storage"""
        if not self.blob_service_client:
            return None
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            download_stream = blob_client.download_blob()
            return download_stream.readall()
            
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None
    
    async def delete_file(self, container_name: str, blob_name: str) -> bool:
        """Delete a file from blob storage"""
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name} from {container_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def list_files(
        self,
        container_type: str,
        company_id: Optional[int] = None,
        prefix: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """List files in a container with optional filtering"""
        if not self.blob_service_client:
            return []
        
        container_name = self.CONTAINERS.get(container_type)
        if not container_name:
            return []
        
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            
            # Build prefix for filtering
            if company_id:
                prefix = f"company_{company_id}/"
            elif prefix:
                prefix = prefix
            
            blobs = []
            for blob in container_client.list_blobs(name_starts_with=prefix):
                blobs.append({
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified,
                    "content_type": blob.content_settings.content_type if blob.content_settings else None,
                    "metadata": blob.metadata,
                    "url": self.get_blob_url(container_name, blob.name)
                })
            
            return blobs
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def validate_file_size(self, file_size: int, max_size_mb: int = 10) -> bool:
        """Validate file size is within limits"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path components
        filename = os.path.basename(filename)
        # Keep only safe characters
        return "".join(c for c in filename if c.isalnum() or c in ".-_")


# Singleton instance
blob_storage_service = BlobStorageService()