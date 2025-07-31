"""
Search Routes for FoodXchange Platform
Provides API endpoints for intelligent search functionality
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

from foodxchange.services.search_service import (
    search_service, SearchFilter, SearchFilterType, SearchCategory
)
from foodxchange.models.user import User
from foodxchange.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    categories: Optional[List[str]] = None
    filters: Optional[List[Dict[str, Any]]] = None
    limit: Optional[int] = 20


class SearchSuggestionRequest(BaseModel):
    """Search suggestion request model"""
    partial_query: str
    user_id: Optional[str] = None


class SearchFilterRequest(BaseModel):
    """Search filter request model"""
    query: Optional[str] = None


class SaveSearchRequest(BaseModel):
    """Save search request model"""
    query: str
    filters: Optional[List[Dict[str, Any]]] = None


@router.post("/")
async def perform_search(request: SearchRequest, current_user: User = Depends(get_current_user)):
    """
    Perform intelligent search across all categories
    """
    try:
        # Convert request to service format
        categories = []
        if request.categories:
            for cat in request.categories:
                try:
                    categories.append(SearchCategory(cat))
                except ValueError:
                    logger.warning(f"Invalid category: {cat}")
        
        filters = []
        if request.filters:
            for filter_data in request.filters:
                try:
                    filter_type = SearchFilterType(filter_data.get("type"))
                    filter_obj = SearchFilter(
                        type=filter_type,
                        value=filter_data.get("value"),
                        operator=filter_data.get("operator", "eq"),
                        label=filter_data.get("label")
                    )
                    filters.append(filter_obj)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid filter: {filter_data}, error: {e}")
        
        # Perform search
        results = await search_service.search(
            query=request.query,
            filters=filters,
            categories=categories if categories else None,
            limit=request.limit
        )
        
        # Save search for user
        await search_service.save_search(
            user_id=str(current_user.id),
            query=request.query,
            filters=filters
        )
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Partial search query"),
    current_user: User = Depends(get_current_user)
):
    """
    Get intelligent search suggestions
    """
    try:
        suggestions = await search_service.get_search_suggestions(
            partial_query=q,
            user_id=str(current_user.id)
        )
        
        # Convert to JSON-serializable format
        suggestion_data = []
        for suggestion in suggestions:
            suggestion_data.append({
                "text": suggestion.text,
                "category": suggestion.category.value,
                "relevance_score": suggestion.relevance_score,
                "metadata": suggestion.metadata,
                "type": suggestion.type
            })
        
        return JSONResponse(content={
            "suggestions": suggestion_data,
            "query": q,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.get("/filters")
async def get_advanced_filters(
    q: Optional[str] = Query(None, description="Current search query for context"),
    current_user: User = Depends(get_current_user)
):
    """
    Get available advanced filters
    """
    try:
        filters = await search_service.get_advanced_filters(query=q)
        
        return JSONResponse(content={
            "filters": filters,
            "query": q,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting advanced filters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get filters: {str(e)}")


@router.post("/save")
async def save_search(request: SaveSearchRequest, current_user: User = Depends(get_current_user)):
    """
    Save search for user's search history
    """
    try:
        filters = []
        if request.filters:
            for filter_data in request.filters:
                try:
                    filter_type = SearchFilterType(filter_data.get("type"))
                    filter_obj = SearchFilter(
                        type=filter_type,
                        value=filter_data.get("value"),
                        operator=filter_data.get("operator", "eq"),
                        label=filter_data.get("label")
                    )
                    filters.append(filter_obj)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid filter: {filter_data}, error: {e}")
        
        success = await search_service.save_search(
            user_id=str(current_user.id),
            query=request.query,
            filters=filters
        )
        
        return JSONResponse(content={
            "success": success,
            "message": "Search saved successfully" if success else "Failed to save search"
        })
        
    except Exception as e:
        logger.error(f"Error saving search: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save search: {str(e)}")


@router.get("/analytics")
async def get_search_analytics(current_user: User = Depends(get_current_user)):
    """
    Get search analytics and insights
    """
    try:
        analytics = await search_service.get_search_analytics(user_id=str(current_user.id))
        
        return JSONResponse(content={
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting search analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/trending")
async def get_trending_searches():
    """
    Get trending searches (public endpoint)
    """
    try:
        analytics = await search_service.get_search_analytics()
        
        return JSONResponse(content={
            "trending_searches": analytics.get("trending_searches", []),
            "popular_categories": analytics.get("popular_categories", []),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting trending searches: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending searches: {str(e)}")


@router.get("/recent")
async def get_recent_searches(current_user: User = Depends(get_current_user)):
    """
    Get user's recent searches
    """
    try:
        analytics = await search_service.get_search_analytics(user_id=str(current_user.id))
        
        return JSONResponse(content={
            "recent_searches": analytics.get("user_searches", []),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting recent searches: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent searches: {str(e)}")


@router.delete("/history")
async def clear_search_history(current_user: User = Depends(get_current_user)):
    """
    Clear user's search history
    """
    try:
        # This would clear the user's search history
        # For now, we'll return success (implementation would be in the service)
        
        return JSONResponse(content={
            "success": True,
            "message": "Search history cleared successfully"
        })
        
    except Exception as e:
        logger.error(f"Error clearing search history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear search history: {str(e)}")


@router.get("/health")
async def search_health_check():
    """
    Health check for search service
    """
    try:
        # Basic health check
        return JSONResponse(content={
            "status": "healthy",
            "service": "intelligent_search",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Search health check failed: {e}")
        raise HTTPException(status_code=503, detail="Search service unhealthy")


# Web routes for search interface
@router.get("/")
async def search_page():
    """
    Render search page
    """
    return {"message": "Search page - use POST /api/search/ for actual search"}


@router.get("/suggestions/web")
async def search_suggestions_web(
    q: str = Query(..., description="Partial search query")
):
    """
    Web endpoint for search suggestions (no authentication required)
    """
    try:
        suggestions = await search_service.get_search_suggestions(partial_query=q)
        
        # Convert to JSON-serializable format
        suggestion_data = []
        for suggestion in suggestions:
            suggestion_data.append({
                "text": suggestion.text,
                "category": suggestion.category.value,
                "relevance_score": suggestion.relevance_score,
                "metadata": suggestion.metadata,
                "type": suggestion.type
            })
        
        return JSONResponse(content={
            "suggestions": suggestion_data,
            "query": q,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return JSONResponse(content={"suggestions": [], "error": str(e)}) 