"""
Help System API Routes

Provides endpoints for:
- Interactive tooltips
- Contextual help suggestions
- Help content search
- Help analytics
- User session management
- Feedback collection
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from foodxchange.services.help_service import (
    help_service, HelpType, HelpCategory, HelpPriority, UserSkillLevel,
    HelpContent, HelpSuggestion, UserHelpSession
)

router = APIRouter(prefix="/api/help", tags=["Help System"])


# Pydantic models for API requests/responses
class HelpContentRequest(BaseModel):
    title: str
    content: str
    help_type: HelpType
    category: HelpCategory
    priority: HelpPriority
    target_element: Optional[str] = None
    page_url: Optional[str] = None
    skill_level: UserSkillLevel = UserSkillLevel.BEGINNER
    tags: List[str] = []
    video_url: Optional[str] = None
    interactive_steps: List[Dict] = []
    related_content: List[str] = []


class HelpContentResponse(BaseModel):
    id: str
    title: str
    content: str
    help_type: HelpType
    category: HelpCategory
    priority: HelpPriority
    target_element: Optional[str] = None
    page_url: Optional[str] = None
    skill_level: UserSkillLevel
    tags: List[str]
    video_url: Optional[str] = None
    interactive_steps: List[Dict]
    related_content: List[str]
    created_at: datetime
    updated_at: datetime
    usage_count: int
    helpful_count: int
    not_helpful_count: int


class HelpSuggestionResponse(BaseModel):
    content_id: str
    title: str
    relevance_score: float
    reason: str
    help_type: HelpType
    priority: HelpPriority


class ContextualHelpRequest(BaseModel):
    page_url: str
    target_element: Optional[str] = None
    user_query: Optional[str] = None
    user_id: Optional[str] = None


class HelpSearchRequest(BaseModel):
    query: str
    category: Optional[HelpCategory] = None
    help_type: Optional[HelpType] = None
    user_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    content_id: str
    helpful: bool
    user_id: Optional[str] = None


class SessionRequest(BaseModel):
    user_id: Optional[str] = None
    page_url: Optional[str] = None


class AnalyticsResponse(BaseModel):
    total_sessions: int
    total_time_spent: int
    average_session_time: float
    total_content_accessed: int
    average_content_per_session: float
    most_accessed_content: List[tuple]
    search_queries: List[str]
    period_days: int


# Helper function to get current user ID (placeholder)
def get_current_user_id(request: Request) -> Optional[str]:
    """Get current user ID from request (placeholder implementation)"""
    # In a real implementation, this would extract user ID from JWT token or session
    return request.headers.get("X-User-ID")


# API Endpoints

@router.get("/tooltip/{element_id}")
async def get_tooltip_content(
    element_id: str,
    page_url: str = Query(..., description="Current page URL"),
    user_id: Optional[str] = Depends(get_current_user_id)
) -> Optional[HelpContentResponse]:
    """Get tooltip content for a specific element"""
    content = help_service.get_tooltip_content(element_id, page_url, user_id)
    if not content:
        return None
    
    return HelpContentResponse(**content.__dict__)


@router.post("/contextual")
async def get_contextual_help(
    request: ContextualHelpRequest
) -> List[HelpSuggestionResponse]:
    """Get contextual help suggestions based on current page and context"""
    suggestions = help_service.get_contextual_help(
        page_url=request.page_url,
        target_element=request.target_element,
        user_id=request.user_id,
        user_query=request.user_query
    )
    
    return [HelpSuggestionResponse(**suggestion.__dict__) for suggestion in suggestions]


@router.post("/search")
async def search_help_content(
    request: HelpSearchRequest
) -> List[HelpContentResponse]:
    """Search help content based on query and filters"""
    results = help_service.search_help_content(
        query=request.query,
        category=request.category,
        help_type=request.help_type,
        user_id=request.user_id
    )
    
    return [HelpContentResponse(**content.__dict__) for content in results]


@router.get("/content/{content_id}")
async def get_help_content(content_id: str) -> HelpContentResponse:
    """Get specific help content by ID"""
    content = help_service.get_help_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Help content not found")
    
    return HelpContentResponse(**content.__dict__)


@router.get("/content/category/{category}")
async def get_help_content_by_category(
    category: HelpCategory
) -> List[HelpContentResponse]:
    """Get all help content for a specific category"""
    content_list = help_service.get_help_content_by_category(category)
    return [HelpContentResponse(**content.__dict__) for content in content_list]


@router.post("/content")
async def create_help_content(
    request: HelpContentRequest
) -> HelpContentResponse:
    """Create new help content"""
    content = HelpContent(
        id=f"help_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        **request.dict()
    )
    
    help_service.add_help_content(content)
    return HelpContentResponse(**content.__dict__)


@router.put("/content/{content_id}")
async def update_help_content(
    content_id: str,
    updates: Dict[str, Any]
) -> HelpContentResponse:
    """Update existing help content"""
    help_service.update_help_content(content_id, updates)
    
    content = help_service.get_help_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Help content not found")
    
    return HelpContentResponse(**content.__dict__)


@router.delete("/content/{content_id}")
async def delete_help_content(content_id: str):
    """Delete help content"""
    content = help_service.get_help_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Help content not found")
    
    help_service.delete_help_content(content_id)
    return {"message": "Help content deleted successfully"}


@router.post("/session/start")
async def start_help_session(
    request: SessionRequest
) -> Dict[str, str]:
    """Start a new help session"""
    session_id = help_service.start_help_session(
        user_id=request.user_id,
        page_url=request.page_url
    )
    return {"session_id": session_id}


@router.post("/session/{session_id}/end")
async def end_help_session(session_id: str):
    """End a help session"""
    help_service.end_help_session(session_id)
    return {"message": "Session ended successfully"}


@router.post("/session/{session_id}/access")
async def record_help_access(
    session_id: str,
    content_id: str
):
    """Record help content access in session"""
    help_service.record_help_access(session_id, content_id)
    return {"message": "Access recorded successfully"}


@router.post("/session/{session_id}/search")
async def record_search_query(
    session_id: str,
    query: str
):
    """Record search query in session"""
    help_service.record_search_query(session_id, query)
    return {"message": "Search query recorded successfully"}


@router.post("/feedback")
async def record_feedback(request: FeedbackRequest):
    """Record user feedback on help content"""
    help_service.record_feedback(
        content_id=request.content_id,
        helpful=request.helpful,
        user_id=request.user_id
    )
    return {"message": "Feedback recorded successfully"}


@router.get("/analytics")
async def get_help_analytics(
    user_id: Optional[str] = Depends(get_current_user_id),
    days: int = Query(30, description="Number of days to analyze")
) -> AnalyticsResponse:
    """Get help system analytics"""
    analytics = help_service.get_help_analytics(user_id=user_id, days=days)
    return AnalyticsResponse(**analytics)


@router.get("/categories")
async def get_help_categories() -> List[Dict[str, str]]:
    """Get all available help categories"""
    return [
        {"value": category.value, "label": category.value.replace("_", " ").title()}
        for category in HelpCategory
    ]


@router.get("/types")
async def get_help_types() -> List[Dict[str, str]]:
    """Get all available help types"""
    return [
        {"value": help_type.value, "label": help_type.value.replace("_", " ").title()}
        for help_type in HelpType
    ]


@router.get("/priorities")
async def get_help_priorities() -> List[Dict[str, str]]:
    """Get all available help priorities"""
    return [
        {"value": priority.value, "label": priority.value.title()}
        for priority in HelpPriority
    ]


@router.get("/skill-levels")
async def get_skill_levels() -> List[Dict[str, str]]:
    """Get all available skill levels"""
    return [
        {"value": level.value, "label": level.value.title()}
        for level in UserSkillLevel
    ]


@router.post("/user/skill-level")
async def update_user_skill_level(
    user_id: str,
    skill_level: UserSkillLevel
):
    """Update user skill level for personalized help"""
    help_service.update_user_skill_level(user_id, skill_level)
    return {"message": "Skill level updated successfully"}


@router.get("/export")
async def export_help_content() -> Dict[str, Any]:
    """Export all help content for backup"""
    return help_service.export_help_content()


@router.post("/import")
async def import_help_content(data: Dict[str, Any]):
    """Import help content from backup"""
    help_service.import_help_content(data)
    return {"message": "Help content imported successfully"}


@router.get("/health")
async def help_system_health_check() -> Dict[str, Any]:
    """Health check for help system"""
    total_content = len(help_service.help_content)
    total_sessions = len(help_service.user_sessions)
    
    return {
        "status": "healthy",
        "total_help_content": total_content,
        "total_sessions": total_sessions,
        "service": "IntelligentHelpService",
        "timestamp": datetime.now().isoformat()
    }


# Web Routes for Help Center UI

@router.get("/center", response_class=HTMLResponse)
async def help_center_page():
    """Help center main page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Help Center - FoodXchange</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .help-category-card {
                transition: transform 0.2s;
                cursor: pointer;
            }
            .help-category-card:hover {
                transform: translateY(-2px);
            }
            .search-highlight {
                background-color: yellow;
                padding: 2px;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <!-- Sidebar -->
                <div class="col-md-3 col-lg-2 bg-light sidebar p-3">
                    <h5 class="mb-3">Help Categories</h5>
                    <div class="list-group list-group-flush" id="categoryList">
                        <!-- Categories will be loaded here -->
                    </div>
                </div>
                
                <!-- Main Content -->
                <div class="col-md-9 col-lg-10">
                    <div class="p-4">
                        <!-- Search Bar -->
                        <div class="row mb-4">
                            <div class="col-12">
                                <div class="input-group">
                                    <input type="text" class="form-control" id="searchInput" 
                                           placeholder="Search help content...">
                                    <button class="btn btn-primary" type="button" onclick="searchHelp()">
                                        <i class="fas fa-search"></i> Search
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Content Area -->
                        <div id="contentArea">
                            <div class="text-center text-muted">
                                <i class="fas fa-question-circle fa-3x mb-3"></i>
                                <h4>How can we help you?</h4>
                                <p>Search for help content or browse categories to get started.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Help Center JavaScript functionality
            let currentSessionId = null;
            
            // Initialize help center
            document.addEventListener('DOMContentLoaded', function() {
                startHelpSession();
                loadCategories();
            });
            
            async function startHelpSession() {
                try {
                    const response = await fetch('/api/help/session/start', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({page_url: window.location.pathname})
                    });
                    const data = await response.json();
                    currentSessionId = data.session_id;
                } catch (error) {
                    console.error('Failed to start help session:', error);
                }
            }
            
            async function loadCategories() {
                try {
                    const response = await fetch('/api/help/categories');
                    const categories = await response.json();
                    
                    const categoryList = document.getElementById('categoryList');
                    categoryList.innerHTML = '';
                    
                    categories.forEach(category => {
                        const item = document.createElement('a');
                        item.href = '#';
                        item.className = 'list-group-item list-group-item-action';
                        item.textContent = category.label;
                        item.onclick = () => loadCategoryContent(category.value);
                        categoryList.appendChild(item);
                    });
                } catch (error) {
                    console.error('Failed to load categories:', error);
                }
            }
            
            async function loadCategoryContent(category) {
                try {
                    const response = await fetch(`/api/help/content/category/${category}`);
                    const content = await response.json();
                    displayContent(content);
                } catch (error) {
                    console.error('Failed to load category content:', error);
                }
            }
            
            async function searchHelp() {
                const query = document.getElementById('searchInput').value;
                if (!query.trim()) return;
                
                try {
                    const response = await fetch('/api/help/search', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query})
                    });
                    const content = await response.json();
                    displayContent(content);
                    
                    // Record search query
                    if (currentSessionId) {
                        await fetch(`/api/help/session/${currentSessionId}/search`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({query: query})
                        });
                    }
                } catch (error) {
                    console.error('Failed to search help content:', error);
                }
            }
            
            function displayContent(contentList) {
                const contentArea = document.getElementById('contentArea');
                
                if (contentList.length === 0) {
                    contentArea.innerHTML = `
                        <div class="text-center text-muted">
                            <i class="fas fa-search fa-3x mb-3"></i>
                            <h4>No help content found</h4>
                            <p>Try a different search term or browse categories.</p>
                        </div>
                    `;
                    return;
                }
                
                contentArea.innerHTML = contentList.map(content => `
                    <div class="card mb-3">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">${content.title}</h5>
                            <span class="badge bg-${getPriorityColor(content.priority)}">${content.priority}</span>
                        </div>
                        <div class="card-body">
                            <p>${content.content}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="small text-muted">
                                    <i class="fas fa-tag me-1"></i>${content.category.replace('_', ' ')}
                                    <span class="ms-3"><i class="fas fa-eye me-1"></i>${content.usage_count}</span>
                                </div>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-success" onclick="recordFeedback('${content.id}', true)">
                                        <i class="fas fa-thumbs-up"></i> Helpful
                                    </button>
                                    <button class="btn btn-outline-danger" onclick="recordFeedback('${content.id}', false)">
                                        <i class="fas fa-thumbs-down"></i> Not Helpful
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
            
            function getPriorityColor(priority) {
                switch (priority) {
                    case 'critical': return 'danger';
                    case 'high': return 'warning';
                    case 'medium': return 'info';
                    case 'low': return 'secondary';
                    default: return 'secondary';
                }
            }
            
            async function recordFeedback(contentId, helpful) {
                try {
                    await fetch('/api/help/feedback', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            content_id: contentId,
                            helpful: helpful
                        })
                    });
                    
                    // Show feedback confirmation
                    const button = event.target;
                    const originalText = button.innerHTML;
                    button.innerHTML = helpful ? '<i class="fas fa-check"></i> Thank you!' : '<i class="fas fa-times"></i> Noted';
                    button.disabled = true;
                    
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.disabled = false;
                    }, 2000);
                } catch (error) {
                    console.error('Failed to record feedback:', error);
                }
            }
            
            // Search on Enter key
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchHelp();
                }
            });
        </script>
    </body>
    </html>
    """ 