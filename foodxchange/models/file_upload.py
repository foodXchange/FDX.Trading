"""File Upload model for tracking CSV/Excel imports"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, JSON
from foodxchange.models.base import Base
from foodxchange.models.mixins import TimestampMixin, AuditMixin
import enum


class UploadStatus(str, enum.Enum):
    """Status of file upload processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class FileType(str, enum.Enum):
    """Supported file types"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class DataType(str, enum.Enum):
    """Type of data being imported"""
    BUYERS = "buyers"
    SUPPLIERS = "suppliers"
    PRODUCTS = "products"
    ORDERS = "orders"


class FileUpload(Base, TimestampMixin, AuditMixin):
    """Model for tracking file uploads and imports"""
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    
    # Import information
    data_type = Column(Enum(DataType), nullable=False)
    status = Column(Enum(UploadStatus), default=UploadStatus.PENDING, nullable=False)
    
    # Processing statistics
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    successful_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    
    # Column mapping used for import
    column_mapping = Column(JSON, nullable=True)
    
    # Processing details
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    
    # Additional metadata
    file_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename='{self.filename}', status={self.status})>"
    
    @property
    def processing_duration(self):
        """Calculate processing duration in seconds"""
        if self.processing_started_at and self.processing_completed_at:
            delta = self.processing_completed_at - self.processing_started_at
            return delta.total_seconds()
        return None
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.processed_rows > 0:
            return (self.successful_rows / self.processed_rows) * 100
        return 0