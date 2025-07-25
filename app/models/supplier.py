from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, JSON, func, ARRAY, Float, Text
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Supplier(Base):
    """Supplier model for FoodXchange platform."""
    __tablename__ = "suppliers"

    id: int = Column(Integer, primary_key=True, index=True)
    
    # Company information - updated field names to match usage
    name: str = Column(String(255), nullable=False)  # Changed from company_name
    company_name: str = Column(String(255))  # Keep for compatibility
    email: str = Column(String(255))
    phone: str = Column(String(50))
    website: str = Column(String(500))  # Added website field
    
    # Location
    country: str = Column(String(100))
    location: str = Column(String(255))  # Added location field
    address: str = Column(Text)
    
    # Business details
    categories = Column(ARRAY(String))
    products: str = Column(Text)  # Comma-separated list of main products
    certifications = Column(ARRAY(String))
    delivery_days: int = Column(Integer)  # Added delivery capability
    moq: float = Column(Float)  # Minimum order quantity
    
    # Ratings and verification
    rating = Column(Numeric(3,2))
    is_verified: bool = Column(Boolean, default=False)
    is_active: bool = Column(Boolean, default=True)  # Added active status
    
    # AI enrichment
    ai_enriched: bool = Column(Boolean, default=False)
    enrichment_data = Column(JSON)
    
    # Additional data
    notes: str = Column(Text)  # Added for agent updates
    tags = Column(JSON)  # Additional tags/keywords
    
    # Scraping metadata
    last_scraped: datetime.datetime = Column(DateTime)  # When website was last scraped
    
    # Timestamps
    created_at: datetime.datetime = Column(DateTime, default=func.now())
    updated_at: datetime.datetime = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    products_catalog = relationship("Product", back_populates="supplier", cascade="all, delete-orphan") 