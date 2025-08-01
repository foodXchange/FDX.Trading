"""Enhanced Project model for FoodXchange sourcing lifecycle tracking"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum
from .base import Base


class ProjectStatus(enum.Enum):
    """Overall project status"""
    INITIATED = "Product Search Initiated"
    IN_PROGRESS = "In Progress"
    REVIEW = "Under Review"
    APPROVED = "Approved"
    PARTIALLY_APPROVED = "Partially Approved"
    REJECTED = "Not Approved"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class StageStatus(enum.Enum):
    """Individual stage status"""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"


class Priority(enum.Enum):
    """Project priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class Project(Base):
    """Enhanced Project model to track the entire sourcing lifecycle"""
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}
    
    # Basic Information
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), unique=True, nullable=False, index=True)  # Auto-generated unique ID
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Buyer Information
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False, index=True)
    buyer_company = Column(String(255), nullable=True)  # Denormalized for quick access
    
    # Project Metadata
    status = Column(Enum(ProjectStatus), default=ProjectStatus.INITIATED, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    current_stage = Column(Integer, default=1)  # Current stage number (1-5)
    completion_percentage = Column(Float, default=0.0)
    
    # Product Information
    total_products_sourced = Column(Integer, default=0)
    approved_products_count = Column(Integer, default=0)
    budget_range_min = Column(Float, nullable=True)
    budget_range_max = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Search/Analysis Data
    search_type = Column(String(50), nullable=True)  # image, url, text
    initial_product_images = Column(JSON, nullable=True)  # URLs of uploaded images
    product_specifications = Column(JSON, nullable=True)  # Detailed specs
    analysis_results = Column(JSON, nullable=True)  # AI analysis results
    
    # Additional Data
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags for filtering
    attachments = Column(JSON, nullable=True)  # List of document URLs
    
    # Flags
    is_active = Column(Boolean, default=True)
    is_urgent = Column(Boolean, default=False)
    has_issues = Column(Boolean, default=False)
    
    # Relationships
    buyer = relationship("Buyer", back_populates="projects")
    project_lines = relationship("ProjectLine", back_populates="project", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.project_id:
            self.project_id = self.generate_project_id()
        if not self.target_completion_date:
            self.target_completion_date = datetime.utcnow() + timedelta(days=30)
    
    def generate_project_id(self):
        """Generate unique project ID: FXP-YYYYMMDD-XXXX"""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        # In production, get the last project number for today and increment
        # For now, use timestamp
        timestamp = datetime.utcnow().strftime("%H%M%S")
        return f"FXP-{date_str}-{timestamp}"
    
    def calculate_completion_percentage(self):
        """Calculate overall project completion based on stages"""
        if not self.project_lines:
            return 0.0
        
        completed_stages = sum(1 for line in self.project_lines 
                             if line.stage_status == StageStatus.COMPLETED)
        total_stages = len(self.project_lines)
        
        if total_stages == 0:
            return 0.0
        
        return (completed_stages / total_stages) * 100
    
    def get_current_stage_name(self):
        """Get the name of the current stage"""
        stage_names = {
            1: "Buyer Request",
            2: "Supplier Search",
            3: "Products in Portfolio",
            4: "Proposals & Samples",
            5: "Project Decision"
        }
        return stage_names.get(self.current_stage, "Unknown")
    
    def advance_stage(self):
        """Advance to the next stage if current stage is completed"""
        current_line = next((line for line in self.project_lines 
                           if line.stage_number == self.current_stage), None)
        
        if current_line and current_line.stage_status == StageStatus.COMPLETED:
            if self.current_stage < 5:
                self.current_stage += 1
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def __repr__(self):
        return f"<Project(id={self.id}, project_id='{self.project_id}', name='{self.name}', status={self.status.value})>"


class ProjectLine(Base):
    """Individual stage tracking for projects"""
    __tablename__ = "project_lines"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Stage Information
    stage_number = Column(Integer, nullable=False)  # 1-5
    stage_name = Column(String(100), nullable=False)
    stage_status = Column(Enum(StageStatus), default=StageStatus.NOT_STARTED, nullable=False)
    
    # Stage-specific Data (JSON for flexibility)
    stage_data = Column(JSON, nullable=True)
    """
    Stage 1 (Buyer Request): {
        "product_images": [], "specifications": {}, "quantity": 0, 
        "target_price": {}, "delivery_timeline": "", "quality_standards": []
    }
    Stage 2 (Supplier Search): {
        "suppliers_contacted": 0, "suppliers_shortlisted": [], 
        "response_rate": 0, "geographic_coverage": []
    }
    Stage 3 (Products in Portfolio): {
        "products_matched": [], "alternative_options": [], 
        "comparison_matrix": {}, "availability_status": {}
    }
    Stage 4 (Proposals & Samples): {
        "proposals_received": 0, "samples_requested": 0, "samples_received": 0,
        "samples_tested": 0, "negotiations": [], "terms": {}
    }
    Stage 5 (Project Decision): {
        "approved_products": [], "rejected_products": [], "rejection_reasons": {},
        "final_suppliers": [], "contract_status": ""
    }
    """
    
    # Timestamps
    start_date = Column(DateTime(timezone=True), nullable=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    expected_completion = Column(DateTime(timezone=True), nullable=True)
    
    # Additional Fields
    notes = Column(Text, nullable=True)
    blockers = Column(JSON, nullable=True)  # List of blocking issues
    assigned_to = Column(String(255), nullable=True)  # User responsible for this stage
    
    # Relationships
    project = relationship("Project", back_populates="project_lines")
    
    def __init__(self, stage_number, **kwargs):
        super().__init__(**kwargs)
        self.stage_number = stage_number
        self.stage_name = self.get_stage_name(stage_number)
        self.stage_data = self.get_default_stage_data(stage_number)
    
    @staticmethod
    def get_stage_name(stage_number):
        """Get stage name by number"""
        stages = {
            1: "Buyer Request",
            2: "Supplier Search",
            3: "Products in Portfolio",
            4: "Proposals & Samples",
            5: "Project Decision"
        }
        return stages.get(stage_number, "Unknown Stage")
    
    @staticmethod
    def get_default_stage_data(stage_number):
        """Get default data structure for each stage"""
        defaults = {
            1: {
                "product_images": [],
                "specifications": {},
                "quantity_required": 0,
                "target_price_range": {"min": 0, "max": 0, "currency": "USD"},
                "delivery_timeline": "",
                "quality_standards": []
            },
            2: {
                "suppliers_contacted": 0,
                "suppliers_shortlisted": [],
                "response_rate": 0,
                "geographic_coverage": []
            },
            3: {
                "products_matched": [],
                "alternative_options": [],
                "comparison_matrix": {},
                "availability_status": {}
            },
            4: {
                "proposals_received": 0,
                "samples_requested": 0,
                "samples_received": 0,
                "samples_tested": 0,
                "price_negotiations": [],
                "terms_conditions": {}
            },
            5: {
                "approved_products": [],
                "rejected_products": [],
                "rejection_reasons": {},
                "final_suppliers": [],
                "contract_status": "Not Started"
            }
        }
        return defaults.get(stage_number, {})
    
    def update_status(self, new_status: StageStatus):
        """Update stage status with timestamps"""
        self.stage_status = new_status
        
        if new_status == StageStatus.IN_PROGRESS and not self.start_date:
            self.start_date = datetime.utcnow()
        elif new_status == StageStatus.COMPLETED:
            self.completion_date = datetime.utcnow()
    
    def get_duration(self):
        """Get the duration of this stage"""
        if self.start_date and self.completion_date:
            return self.completion_date - self.start_date
        elif self.start_date:
            return datetime.utcnow() - self.start_date
        return None
    
    def __repr__(self):
        return f"<ProjectLine(stage={self.stage_number}, name='{self.stage_name}', status={self.stage_status.value})>"