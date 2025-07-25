"""
Product model for storing supplier product catalogs
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Product(Base):
    """
    Product catalog items from suppliers
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Product identification
    name = Column(String(255), nullable=False, index=True)  # English name
    original_name = Column(String(255))  # Name in original language
    sku = Column(String(100))  # Supplier's SKU/product code
    barcode = Column(String(50))  # EAN/UPC if available
    
    # Product details
    description = Column(Text)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    brand = Column(String(100))
    
    # Pricing
    price = Column(Float)
    currency = Column(String(3), default='USD')  # ISO currency code
    price_per = Column(String(50))  # e.g., "per kg", "per case"
    unit = Column(String(50))  # kg, lb, piece, case, etc.
    
    # Quantity and availability
    moq = Column(Float)  # Minimum order quantity
    quantity_available = Column(Float)
    lead_time_days = Column(Integer)
    
    # Product specifications
    weight = Column(Float)  # In kg
    weight_unit = Column(String(10), default='kg')
    dimensions = Column(String(100))  # L x W x H
    
    # Certifications and compliance
    certifications = Column(JSON)  # List of certifications
    is_organic = Column(Boolean, default=False)
    is_halal = Column(Boolean, default=False)
    is_kosher = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    
    # Images and documents
    image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    spec_sheet_url = Column(String(500))
    
    # Source information
    source_url = Column(String(500))  # Where this was scraped from
    language = Column(String(10))  # Original language code
    confidence_score = Column(Float)  # Extraction confidence (0-1)
    
    # Metadata
    tags = Column(JSON)  # Additional tags/keywords
    attributes = Column(JSON)  # Additional attributes as key-value pairs
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime)  # When this was last scraped/updated
    
    # Company association
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products_catalog")
    company = relationship("Company", back_populates="products")
    
    def __repr__(self):
        return f"<Product {self.name} from {self.supplier_id}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "name": self.name,
            "original_name": self.original_name,
            "sku": self.sku,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "currency": self.currency,
            "unit": self.unit,
            "moq": self.moq,
            "quantity_available": self.quantity_available,
            "lead_time_days": self.lead_time_days,
            "certifications": self.certifications,
            "is_organic": self.is_organic,
            "is_halal": self.is_halal,
            "is_kosher": self.is_kosher,
            "image_url": self.image_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
    
    def matches_requirements(self, requirements: dict) -> float:
        """
        Calculate how well this product matches buyer requirements
        Returns a score between 0 and 1
        """
        score = 0.0
        factors = 0
        
        # Price match
        if 'max_price' in requirements and self.price:
            factors += 1
            if self.price <= requirements['max_price']:
                score += 1.0
            else:
                # Partial score based on how close
                overage = (self.price - requirements['max_price']) / requirements['max_price']
                score += max(0, 1 - overage)
        
        # MOQ match
        if 'quantity' in requirements and self.moq:
            factors += 1
            if self.moq <= requirements['quantity']:
                score += 1.0
        
        # Certification match
        if 'certifications' in requirements and self.certifications:
            factors += 1
            required_certs = set(requirements['certifications'])
            product_certs = set(self.certifications)
            if required_certs.issubset(product_certs):
                score += 1.0
            else:
                # Partial score based on overlap
                overlap = len(required_certs.intersection(product_certs))
                score += overlap / len(required_certs)
        
        # Delivery time match
        if 'max_lead_time' in requirements and self.lead_time_days:
            factors += 1
            if self.lead_time_days <= requirements['max_lead_time']:
                score += 1.0
        
        return score / factors if factors > 0 else 0.0