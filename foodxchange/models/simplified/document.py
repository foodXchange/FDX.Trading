"""Simplified Document model - file attachments"""
from sqlalchemy import Column, Integer, String, DateTime, func
from foodxchange.database import Base

class Document(Base):
    """Simple document/file storage"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Polymorphic association
    related_id = Column(Integer, nullable=False)
    related_type = Column(String(50), nullable=False)  # 'project', 'user', 'quote'
    
    # File information
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))  # pdf, image, excel, etc.
    url = Column(String(500), nullable=False)  # Cloud storage URL
    
    # Timestamp
    uploaded_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', type='{self.related_type}')>"