"""Import Record model for tracking individual records from file imports"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from foodxchange.models.base import Base
from foodxchange.models.mixins import TimestampMixin
import enum


class RecordStatus(str, enum.Enum):
    """Status of individual import record"""
    SUCCESS = "success"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    UPDATED = "updated"


class ImportRecord(Base, TimestampMixin):
    """Model for tracking individual records from imports"""
    __tablename__ = "import_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to parent upload
    file_upload_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False, index=True)
    file_upload = relationship("FileUpload", backref="import_records")
    
    # Record information
    row_number = Column(Integer, nullable=False)
    status = Column(Enum(RecordStatus), nullable=False)
    
    # Original data from import
    original_data = Column(JSON, nullable=False)
    
    # Processed data (after cleaning/validation)
    processed_data = Column(JSON, nullable=True)
    
    # Error information
    error_message = Column(Text, nullable=True)
    validation_errors = Column(JSON, nullable=True)
    
    # Reference to created/updated entity
    entity_type = Column(String(50), nullable=True)  # 'buyer', 'supplier', etc
    entity_id = Column(String(50), nullable=True)  # ID of created/updated entity
    
    # Flags
    is_duplicate = Column(Boolean, default=False)
    is_updated = Column(Boolean, default=False)
    
    # AI-related fields
    ai_assisted = Column(Boolean, default=False)
    ai_confidence_score = Column(JSON, nullable=True)  # Field-level confidence scores
    ai_mapping_used = Column(JSON, nullable=True)  # The field mappings AI suggested
    ai_cleaning_applied = Column(JSON, nullable=True)  # What cleaning operations were applied
    
    def __repr__(self):
        return f"<ImportRecord(id={self.id}, row={self.row_number}, status={self.status}, ai={self.ai_assisted})>"