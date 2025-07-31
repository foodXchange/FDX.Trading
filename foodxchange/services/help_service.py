"""
AI Tooltips, Help System & Support Center Optimization Service

This service provides intelligent, contextual help and support features including:
- Interactive tooltips with AI-powered content
- Contextual help system
- Support center with self-service capabilities
- Knowledge base management
- User behavior tracking for help optimization
"""

import json
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HelpType(Enum):
    """Types of help content"""
    TOOLTIP = "tooltip"
    CONTEXTUAL = "contextual"
    MODAL = "modal"
    SIDEBAR = "sidebar"
    INLINE = "inline"
    VIDEO = "video"
    INTERACTIVE = "interactive"


class HelpCategory(Enum):
    """Categories of help content"""
    GETTING_STARTED = "getting_started"
    PRODUCT_ANALYSIS = "product_analysis"
    SEARCH = "search"
    DATA_IMPORT = "data_import"
    ACCOUNT_MANAGEMENT = "account_management"
    SECURITY = "security"
    TROUBLESHOOTING = "troubleshooting"
    ADVANCED_FEATURES = "advanced_features"
    API_INTEGRATION = "api_integration"
    GENERAL = "general"


class HelpPriority(Enum):
    """Priority levels for help content"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserSkillLevel(Enum):
    """User skill levels for personalized help"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class HelpContent:
    """Help content structure"""
    id: str
    title: str
    content: str
    help_type: HelpType
    category: HelpCategory
    priority: HelpPriority
    target_element: Optional[str] = None
    page_url: Optional[str] = None
    skill_level: UserSkillLevel = UserSkillLevel.BEGINNER
    tags: List[str] = None
    video_url: Optional[str] = None
    interactive_steps: List[Dict] = None
    related_content: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    usage_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.interactive_steps is None:
            self.interactive_steps = []
        if self.related_content is None:
            self.related_content = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class UserHelpSession:
    """User help session tracking"""
    session_id: str
    user_id: Optional[str]
    page_url: str
    help_content_accessed: List[str]
    search_queries: List[str]
    time_spent: int  # seconds
    session_start: datetime
    session_end: Optional[datetime] = None
    feedback_given: Dict[str, bool] = None  # content_id: helpful

    def __post_init__(self):
        if self.help_content_accessed is None:
            self.help_content_accessed = []
        if self.search_queries is None:
            self.search_queries = []
        if self.feedback_given is None:
            self.feedback_given = {}


@dataclass
class HelpSuggestion:
    """AI-powered help suggestion"""
    content_id: str
    title: str
    relevance_score: float
    reason: str
    help_type: HelpType
    priority: HelpPriority


class IntelligentHelpService:
    """
    Intelligent Help Service providing AI-powered tooltips, contextual help,
    and support center functionality
    """
    
    def __init__(self):
        self.help_content: Dict[str, HelpContent] = {}
        self.user_sessions: Dict[str, UserHelpSession] = {}
        self.user_skill_levels: Dict[str, UserSkillLevel] = {}
        self.help_patterns: Dict[str, List[str]] = {}
        self._initialize_help_content()
        self._initialize_help_patterns()
    
    def _initialize_help_content(self):
        """Initialize default help content"""
        default_content = [
            # Product Analysis Help
            HelpContent(
                id="product_analysis_upload",
                title="Upload Product Images",
                content="Upload clear, high-quality images of your product. Supported formats: JPG, PNG, WEBP (Max 10MB each). Multiple images help AI provide more accurate analysis.",
                help_type=HelpType.TOOLTIP,
                category=HelpCategory.PRODUCT_ANALYSIS,
                priority=HelpPriority.HIGH,
                target_element="#imageUpload",
                page_url="/product-analysis/",
                skill_level=UserSkillLevel.BEGINNER,
                tags=["upload", "images", "file formats", "size limits"]
            ),
            HelpContent(
                id="product_analysis_ai_button",
                title="AI Analysis Process",
                content="Click 'Analyze with AI' to automatically extract product information from your images. The AI will identify product characteristics, nutritional information, and other details. Always review and edit the results for accuracy.",
                help_type=HelpType.CONTEXTUAL,
                category=HelpCategory.PRODUCT_ANALYSIS,
                priority=HelpPriority.HIGH,
                target_element="#analyzeBtn",
                page_url="/product-analysis/",
                skill_level=UserSkillLevel.BEGINNER,
                tags=["ai analysis", "automation", "accuracy", "review"]
            ),
            HelpContent(
                id="product_analysis_editing",
                title="Edit Analysis Results",
                content="All AI-generated fields are editable. Click on any field to modify the content. Your corrections help improve the AI's accuracy for future analyses.",
                help_type=HelpType.INLINE,
                category=HelpCategory.PRODUCT_ANALYSIS,
                priority=HelpPriority.MEDIUM,
                page_url="/product-analysis/",
                skill_level=UserSkillLevel.INTERMEDIATE,
                tags=["editing", "corrections", "ai learning", "accuracy"]
            ),
            
            # Search Help
            HelpContent(
                id="search_intelligent",
                title="Intelligent Search",
                content="Use natural language to search for products, suppliers, or projects. Try phrases like 'organic vegetables in California' or 'certified halal meat suppliers'. The AI understands context and provides relevant suggestions.",
                help_type=HelpType.MODAL,
                category=HelpCategory.SEARCH,
                priority=HelpPriority.HIGH,
                page_url="/",
                skill_level=UserSkillLevel.BEGINNER,
                tags=["natural language", "ai search", "suggestions", "context"]
            ),
            HelpContent(
                id="search_filters",
                title="Advanced Filters",
                content="Use filters to narrow your search results by location, certifications, company size, and product category. Combine multiple filters for precise results.",
                help_type=HelpType.SIDEBAR,
                category=HelpCategory.SEARCH,
                priority=HelpPriority.MEDIUM,
                page_url="/",
                skill_level=UserSkillLevel.INTERMEDIATE,
                tags=["filters", "refinement", "location", "certifications"]
            ),
            
            # Data Import Help
            HelpContent(
                id="data_import_formats",
                title="Supported File Formats",
                content="Import your product data using CSV or Excel files (XLSX, XLS). Ensure your file has headers and follows the required column structure. Maximum file size: 10MB.",
                help_type=HelpType.TOOLTIP,
                category=HelpCategory.DATA_IMPORT,
                priority=HelpPriority.HIGH,
                page_url="/data-import/",
                skill_level=UserSkillLevel.BEGINNER,
                tags=["csv", "excel", "file formats", "import"]
            ),
            
            # Account Management Help
            HelpContent(
                id="account_security",
                title="Security Best Practices",
                content="Use a strong, unique password and enable two-factor authentication for enhanced security. Regularly review your active sessions and update your security settings.",
                help_type=HelpType.CONTEXTUAL,
                category=HelpCategory.SECURITY,
                priority=HelpPriority.HIGH,
                page_url="/profile/settings/",
                skill_level=UserSkillLevel.BEGINNER,
                tags=["security", "password", "2fa", "sessions"]
            ),
            
            # Getting Started Help
            HelpContent(
                id="getting_started_welcome",
                title="Welcome to FoodXchange",
                content="Start by analyzing a product image to see how AI can help you. Then explore our intelligent search to find suppliers and products. Need help? Use the help center or contact support.",
                help_type=HelpType.MODAL,
                category=HelpCategory.GETTING_STARTED,
                priority=HelpPriority.CRITICAL,
                page_url="/",
                skill_level=UserSkillLevel.BEGINNER,
                tags=["welcome", "getting started", "first steps"]
            )
        ]
        
        for content in default_content:
            self.help_content[content.id] = content
    
    def _initialize_help_patterns(self):
        """Initialize help patterns for intelligent suggestions"""
        self.help_patterns = {
            "upload": ["upload", "file", "image", "photo", "picture", "add files"],
            "analysis": ["analyze", "ai", "extract", "identify", "detect", "scan"],
            "search": ["find", "search", "look for", "discover", "browse", "explore"],
            "import": ["import", "upload data", "bulk", "csv", "excel", "spreadsheet"],
            "account": ["profile", "settings", "account", "user", "preferences"],
            "security": ["password", "security", "login", "authentication", "2fa"],
            "troubleshooting": ["error", "problem", "issue", "not working", "broken", "failed"],
            "advanced": ["api", "integration", "automation", "workflow", "advanced"]
        }
    
    def get_contextual_help(self, page_url: str, target_element: str = None, 
                           user_id: str = None, user_query: str = None) -> List[HelpSuggestion]:
        """
        Get contextual help suggestions based on current page and user context
        """
        suggestions = []
        
        # Get user skill level
        skill_level = self.user_skill_levels.get(user_id, UserSkillLevel.BEGINNER)
        
        # Find relevant help content
        for content in self.help_content.values():
            if content.page_url == page_url:
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(
                    content, target_element, user_query, skill_level
                )
                
                if relevance_score > 0.3:  # Threshold for relevance
                    suggestions.append(HelpSuggestion(
                        content_id=content.id,
                        title=content.title,
                        relevance_score=relevance_score,
                        reason=self._get_suggestion_reason(content, target_element, user_query),
                        help_type=content.help_type,
                        priority=content.priority
                    ))
        
        # Sort by relevance and priority
        suggestions.sort(key=lambda x: (x.relevance_score, x.priority.value), reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_relevance_score(self, content: HelpContent, target_element: str = None,
                                 user_query: str = None, skill_level: UserSkillLevel = None) -> float:
        """Calculate relevance score for help content"""
        score = 0.0
        
        # Element matching
        if target_element and content.target_element:
            if target_element == content.target_element:
                score += 0.4
            elif target_element in content.target_element or content.target_element in target_element:
                score += 0.2
        
        # Query matching
        if user_query:
            query_lower = user_query.lower()
            content_lower = f"{content.title} {content.content}".lower()
            
            # Direct keyword matching
            for tag in content.tags:
                if tag.lower() in query_lower:
                    score += 0.3
            
            # Pattern matching
            for pattern_key, pattern_words in self.help_patterns.items():
                if any(word in query_lower for word in pattern_words):
                    if pattern_key in content_lower:
                        score += 0.2
        
        # Skill level matching
        if skill_level and content.skill_level == skill_level:
            score += 0.1
        
        # Usage and helpfulness
        if content.usage_count > 0:
            helpfulness_ratio = content.helpful_count / (content.helpful_count + content.not_helpful_count)
            score += helpfulness_ratio * 0.1
        
        return min(score, 1.0)
    
    def _get_suggestion_reason(self, content: HelpContent, target_element: str = None,
                             user_query: str = None) -> str:
        """Get human-readable reason for suggestion"""
        reasons = []
        
        if target_element and content.target_element == target_element:
            reasons.append("Direct element match")
        
        if user_query:
            matching_tags = [tag for tag in content.tags if tag.lower() in user_query.lower()]
            if matching_tags:
                reasons.append(f"Matches your query about {', '.join(matching_tags)}")
        
        if content.priority == HelpPriority.CRITICAL:
            reasons.append("Critical information for this feature")
        elif content.priority == HelpPriority.HIGH:
            reasons.append("Important for getting started")
        
        return "; ".join(reasons) if reasons else "Relevant to your current context"
    
    def get_tooltip_content(self, element_id: str, page_url: str, user_id: str = None) -> Optional[HelpContent]:
        """Get tooltip content for a specific element"""
        for content in self.help_content.values():
            if (content.help_type == HelpType.TOOLTIP and 
                content.target_element == element_id and 
                content.page_url == page_url):
                self._increment_usage(content.id)
                return content
        return None
    
    def search_help_content(self, query: str, category: HelpCategory = None, 
                          help_type: HelpType = None, user_id: str = None) -> List[HelpContent]:
        """Search help content based on query and filters"""
        results = []
        query_lower = query.lower()
        
        for content in self.help_content.values():
            # Apply filters
            if category and content.category != category:
                continue
            if help_type and content.help_type != help_type:
                continue
            
            # Search in title, content, and tags
            searchable_text = f"{content.title} {content.content} {' '.join(content.tags)}".lower()
            
            if query_lower in searchable_text:
                results.append(content)
                self._increment_usage(content.id)
        
        # Sort by relevance and priority
        results.sort(key=lambda x: (x.priority.value, x.usage_count), reverse=True)
        
        return results
    
    def get_help_analytics(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get help system analytics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter sessions by date
        recent_sessions = [
            session for session in self.user_sessions.values()
            if session.session_start >= cutoff_date
        ]
        
        if user_id:
            recent_sessions = [s for s in recent_sessions if s.user_id == user_id]
        
        # Calculate analytics
        total_sessions = len(recent_sessions)
        total_time_spent = sum(s.time_spent for s in recent_sessions)
        total_content_accessed = sum(len(s.help_content_accessed) for s in recent_sessions)
        
        # Most accessed content
        content_access_count = {}
        for session in recent_sessions:
            for content_id in session.help_content_accessed:
                content_access_count[content_id] = content_access_count.get(content_id, 0) + 1
        
        most_accessed = sorted(content_access_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Search analytics
        search_queries = []
        for session in recent_sessions:
            search_queries.extend(session.search_queries)
        
        return {
            "total_sessions": total_sessions,
            "total_time_spent": total_time_spent,
            "average_session_time": total_time_spent / total_sessions if total_sessions > 0 else 0,
            "total_content_accessed": total_content_accessed,
            "average_content_per_session": total_content_accessed / total_sessions if total_sessions > 0 else 0,
            "most_accessed_content": most_accessed,
            "search_queries": search_queries,
            "period_days": days
        }
    
    def start_help_session(self, user_id: str = None, page_url: str = None) -> str:
        """Start a new help session"""
        session_id = f"help_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id or 'anonymous'}"
        
        session = UserHelpSession(
            session_id=session_id,
            user_id=user_id,
            page_url=page_url or "/",
            session_start=datetime.now()
        )
        
        self.user_sessions[session_id] = session
        return session_id
    
    def end_help_session(self, session_id: str):
        """End a help session"""
        if session_id in self.user_sessions:
            session = self.user_sessions[session_id]
            session.session_end = datetime.now()
            session.time_spent = int((session.session_end - session.session_start).total_seconds())
    
    def record_help_access(self, session_id: str, content_id: str):
        """Record help content access"""
        if session_id in self.user_sessions:
            session = self.user_sessions[session_id]
            if content_id not in session.help_content_accessed:
                session.help_content_accessed.append(content_id)
    
    def record_search_query(self, session_id: str, query: str):
        """Record search query"""
        if session_id in self.user_sessions:
            session = self.user_sessions[session_id]
            session.search_queries.append(query)
    
    def record_feedback(self, content_id: str, helpful: bool, user_id: str = None):
        """Record user feedback on help content"""
        if content_id in self.help_content:
            content = self.help_content[content_id]
            if helpful:
                content.helpful_count += 1
            else:
                content.not_helpful_count += 1
            content.updated_at = datetime.now()
    
    def update_user_skill_level(self, user_id: str, skill_level: UserSkillLevel):
        """Update user skill level for personalized help"""
        self.user_skill_levels[user_id] = skill_level
    
    def add_help_content(self, content: HelpContent):
        """Add new help content"""
        self.help_content[content.id] = content
    
    def update_help_content(self, content_id: str, updates: Dict[str, Any]):
        """Update existing help content"""
        if content_id in self.help_content:
            content = self.help_content[content_id]
            for key, value in updates.items():
                if hasattr(content, key):
                    setattr(content, key, value)
            content.updated_at = datetime.now()
    
    def delete_help_content(self, content_id: str):
        """Delete help content"""
        if content_id in self.help_content:
            del self.help_content[content_id]
    
    def _increment_usage(self, content_id: str):
        """Increment usage count for help content"""
        if content_id in self.help_content:
            self.help_content[content_id].usage_count += 1
    
    def get_help_content_by_id(self, content_id: str) -> Optional[HelpContent]:
        """Get help content by ID"""
        return self.help_content.get(content_id)
    
    def get_help_content_by_category(self, category: HelpCategory) -> List[HelpContent]:
        """Get all help content for a specific category"""
        return [content for content in self.help_content.values() if content.category == category]
    
    def export_help_content(self) -> Dict[str, Any]:
        """Export help content for backup or migration"""
        return {
            "help_content": {k: asdict(v) for k, v in self.help_content.items()},
            "export_date": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def import_help_content(self, data: Dict[str, Any]):
        """Import help content from backup"""
        if "help_content" in data:
            for content_id, content_data in data["help_content"].items():
                # Convert datetime strings back to datetime objects
                if "created_at" in content_data:
                    content_data["created_at"] = datetime.fromisoformat(content_data["created_at"])
                if "updated_at" in content_data:
                    content_data["updated_at"] = datetime.fromisoformat(content_data["updated_at"])
                
                # Recreate HelpContent object
                content = HelpContent(**content_data)
                self.help_content[content_id] = content


# Global instance
help_service = IntelligentHelpService() 