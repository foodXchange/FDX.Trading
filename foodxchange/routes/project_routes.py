"""Enhanced project routes for FoodXchange sourcing lifecycle"""
from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List
import json
import logging
from datetime import datetime

from foodxchange.core.auth import get_current_user, require_auth
from foodxchange.models.project_enhanced import Project, ProjectLine, ProjectStatus, StageStatus, Priority

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_class=HTMLResponse)
@require_auth
async def projects_dashboard(request: Request):
    """Projects dashboard with enhanced tracking"""
    # Import templates locally to avoid circular import
    from fastapi.templating import Jinja2Templates
    from pathlib import Path
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    
    # Add url_for to template context
    def url_for(name: str, **path_params) -> str:
        routes = {
            "static": "/static",
            "projects": "/projects",
            "project_detail": "/projects/{project_id}"
        }
        if name == "static" and "filename" in path_params:
            return f"/static/{path_params['filename']}"
        base_route = routes.get(name, "/")
        for param, value in path_params.items():
            base_route = base_route.replace(f"{{{param}}}", str(value))
        return base_route
    
    templates.env.globals["url_for"] = url_for
    
    user = get_current_user(request)
    
    # Mock projects for now (in production, fetch from database)
    projects = [
        {
            "project_id": "FXP-20240115-001",
            "name": "Organic Honey Sourcing Q1 2024",
            "buyer_company": "Natural Foods Co.",
            "status": "In Progress",
            "current_stage": 3,
            "current_stage_name": "Products in Portfolio",
            "completion_percentage": 60,
            "priority": "High",
            "created_at": "2024-01-15",
            "days_elapsed": 5,
            "total_products": 3,
            "is_urgent": False
        },
        {
            "project_id": "FXP-20240112-002",
            "name": "Gluten-Free Pasta Suppliers",
            "buyer_company": "Health Foods Inc.",
            "status": "Under Review",
            "current_stage": 4,
            "current_stage_name": "Proposals & Samples",
            "completion_percentage": 80,
            "priority": "Medium",
            "created_at": "2024-01-12",
            "days_elapsed": 8,
            "total_products": 5,
            "is_urgent": False
        }
    ]
    
    return templates.TemplateResponse("pages/projects_enhanced.html", {
        "request": request,
        "current_user": {
            "id": user.user_id,
            "email": user.email,
            "role": user.role,
            "is_admin": user.is_admin
        },
        "projects": projects,
        "active_count": len([p for p in projects if p["status"] != "Completed"]),
        "completed_count": len([p for p in projects if p["status"] == "Completed"])
    })


@router.get("/{project_id}", response_class=HTMLResponse)
@require_auth
async def project_detail(request: Request, project_id: str):
    """Detailed project view with timeline"""
    # Import templates locally to avoid circular import
    from fastapi.templating import Jinja2Templates
    from pathlib import Path
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    
    # Add url_for to template context
    def url_for(name: str, **path_params) -> str:
        routes = {
            "static": "/static",
            "projects": "/projects",
            "project_detail": "/projects/{project_id}"
        }
        if name == "static" and "filename" in path_params:
            return f"/static/{path_params['filename']}"
        base_route = routes.get(name, "/")
        for param, value in path_params.items():
            base_route = base_route.replace(f"{{{param}}}", str(value))
        return base_route
    
    templates.env.globals["url_for"] = url_for
    
    user = get_current_user(request)
    
    # Mock project data (in production, fetch from database)
    project = {
        "project_id": project_id,
        "name": "Organic Honey Sourcing Q1 2024",
        "description": "Sourcing organic honey from certified suppliers for Q1 2024 product launch",
        "buyer_company": "Natural Foods Co.",
        "status": "In Progress",
        "priority": "High",
        "current_stage": 3,
        "completion_percentage": 60,
        "created_at": "2024-01-15T10:30:00",
        "target_completion_date": "2024-02-15",
        "budget_range": {"min": 50000, "max": 75000, "currency": "USD"},
        "total_products": 3,
        "approved_products": 0,
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Buyer Request",
                "status": "Completed",
                "start_date": "2024-01-15T10:30:00",
                "completion_date": "2024-01-16T14:20:00",
                "data": {
                    "product_images": ["/uploads/honey1.jpg", "/uploads/honey2.jpg"],
                    "quantity_required": 5000,
                    "quality_standards": ["Organic Certified", "ISO 22000", "Fair Trade"]
                }
            },
            {
                "stage_number": 2,
                "stage_name": "Supplier Search",
                "status": "Completed",
                "start_date": "2024-01-16T14:30:00",
                "completion_date": "2024-01-18T16:45:00",
                "data": {
                    "suppliers_contacted": 15,
                    "suppliers_shortlisted": ["Honey Farm Co.", "Pure Nature Ltd.", "Golden Bee Inc."],
                    "response_rate": 73.3
                }
            },
            {
                "stage_number": 3,
                "stage_name": "Products in Portfolio",
                "status": "In Progress",
                "start_date": "2024-01-18T17:00:00",
                "completion_date": None,
                "data": {
                    "products_matched": ["Wildflower Honey", "Acacia Honey", "Manuka Honey"],
                    "alternative_options": ["Orange Blossom Honey", "Eucalyptus Honey"]
                }
            },
            {
                "stage_number": 4,
                "stage_name": "Proposals & Samples",
                "status": "Not Started",
                "start_date": None,
                "completion_date": None,
                "data": {
                    "proposals_received": 0,
                    "samples_requested": 0
                }
            },
            {
                "stage_number": 5,
                "stage_name": "Project Decision",
                "status": "Not Started",
                "start_date": None,
                "completion_date": None,
                "data": {}
            }
        ],
        "activity_log": [
            {"timestamp": "2024-01-20T10:00:00", "action": "Product comparison matrix updated", "user": "admin@foodxchange.com"},
            {"timestamp": "2024-01-19T15:30:00", "action": "Alternative honey options added", "user": "admin@foodxchange.com"},
            {"timestamp": "2024-01-18T17:00:00", "action": "Stage 3: Products in Portfolio started", "user": "system"},
            {"timestamp": "2024-01-18T16:45:00", "action": "Stage 2: Supplier Search completed", "user": "admin@foodxchange.com"}
        ]
    }
    
    return templates.TemplateResponse("pages/project_detail.html", {
        "request": request,
        "current_user": {
            "id": user.user_id,
            "email": user.email,
            "role": user.role,
            "is_admin": user.is_admin
        },
        "project": project
    })


@router.post("/create")
async def create_project(
    request: Request,
    name: str = Form(...),
    buyer_id: int = Form(...),
    priority: str = Form("medium"),
    description: Optional[str] = Form(None),
    budget_min: Optional[float] = Form(None),
    budget_max: Optional[float] = Form(None)
):
    """Create a new project with automatic stage initialization"""
    try:
        # In production, create in database
        # For now, return mock response
        new_project = {
            "project_id": f"FXP-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}",
            "name": name,
            "buyer_id": buyer_id,
            "priority": priority,
            "status": "Product Search Initiated",
            "stages_created": 5
        }
        
        logger.info(f"Created new project: {new_project['project_id']}")
        
        return JSONResponse(content={
            "success": True,
            "project": new_project,
            "message": "Project created successfully"
        })
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error creating project: {str(e)}"
        }, status_code=500)


@router.post("/{project_id}/stage/{stage_number}/update")
async def update_stage_status(
    request: Request,
    project_id: str,
    stage_number: int,
    status: str = Form(...),
    notes: Optional[str] = Form(None)
):
    """Update the status of a project stage"""
    try:
        # Validate stage number
        if stage_number < 1 or stage_number > 5:
            raise ValueError("Invalid stage number")
        
        # In production, update in database
        # For now, return mock response
        result = {
            "project_id": project_id,
            "stage_number": stage_number,
            "new_status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Updated stage {stage_number} for project {project_id} to {status}")
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": f"Stage {stage_number} updated successfully"
        })
    except Exception as e:
        logger.error(f"Error updating stage: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error updating stage: {str(e)}"
        }, status_code=500)


@router.post("/{project_id}/stage/{stage_number}/data")
async def update_stage_data(
    request: Request,
    project_id: str,
    stage_number: int
):
    """Update stage-specific data"""
    try:
        # Get JSON data from request body
        stage_data = await request.json()
        
        # In production, update in database
        # For now, return mock response
        result = {
            "project_id": project_id,
            "stage_number": stage_number,
            "data_updated": True,
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Updated data for stage {stage_number} in project {project_id}")
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": "Stage data updated successfully"
        })
    except Exception as e:
        logger.error(f"Error updating stage data: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error updating stage data: {str(e)}"
        }, status_code=500)


@router.get("/api/list")
async def list_projects(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    buyer_id: Optional[int] = None
):
    """API endpoint to list projects with filters"""
    try:
        # In production, query from database with filters
        # For now, return mock data
        projects = [
            {
                "project_id": "FXP-20240115-001",
                "name": "Organic Honey Sourcing Q1 2024",
                "buyer_company": "Natural Foods Co.",
                "status": "In Progress",
                "priority": "High",
                "current_stage": 3,
                "completion_percentage": 60,
                "created_at": "2024-01-15T10:30:00",
                "total_products": 3
            }
        ]
        
        return JSONResponse(content={
            "success": True,
            "projects": projects,
            "total": len(projects)
        })
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error listing projects: {str(e)}"
        }, status_code=500)


@router.post("/api/create-from-analysis")
async def create_project_from_analysis(request: Request):
    """Create a project automatically from product analysis"""
    try:
        # Get analysis data from request
        analysis_data = await request.json()
        
        # Extract relevant information
        project_data = {
            "name": f"Product Sourcing - {analysis_data.get('product_name', 'Unknown')}",
            "buyer_id": analysis_data.get('buyer_id', 1),
            "priority": "medium",
            "search_type": "image",
            "initial_product_images": analysis_data.get('images', []),
            "product_specifications": analysis_data.get('specifications', {}),
            "analysis_results": analysis_data.get('analysis', {})
        }
        
        # Create project with initial stage data
        new_project = {
            "project_id": f"FXP-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}",
            "name": project_data["name"],
            "status": "Product Search Initiated",
            "current_stage": 1,
            "stage_1_data": {
                "product_images": project_data["initial_product_images"],
                "specifications": project_data["product_specifications"]
            }
        }
        
        logger.info(f"Created project from analysis: {new_project['project_id']}")
        
        return JSONResponse(content={
            "success": True,
            "project": new_project,
            "message": "Project created from product analysis"
        })
    except Exception as e:
        logger.error(f"Error creating project from analysis: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error creating project: {str(e)}"
        }, status_code=500)


@router.post("/{project_id}/advance")
async def advance_project_stage(request: Request, project_id: str):
    """Advance project to next stage"""
    try:
        # In production, update in database
        # For now, return mock response
        result = {
            "project_id": project_id,
            "previous_stage": 3,
            "new_stage": 4,
            "new_stage_name": "Proposals & Samples",
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Advanced project {project_id} to next stage")
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": "Project advanced to next stage successfully"
        })
    except Exception as e:
        logger.error(f"Error advancing project stage: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error advancing stage: {str(e)}"
        }, status_code=500)


@router.post("/{project_id}/note")
async def add_project_note(request: Request, project_id: str):
    """Add a note to project"""
    try:
        # Get note data from request
        data = await request.json()
        note_text = data.get("note", "")
        
        if not note_text:
            raise ValueError("Note text is required")
        
        # In production, save to database
        # For now, return mock response
        result = {
            "project_id": project_id,
            "note_id": f"NOTE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "note": note_text,
            "created_by": get_current_user(request).email,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Added note to project {project_id}")
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": "Note added successfully"
        })
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error adding note: {str(e)}"
        }, status_code=500)


@router.post("/{project_id}/document")
async def upload_project_document(request: Request, project_id: str):
    """Upload document to project"""
    try:
        # In production, handle file upload
        # For now, return mock response
        result = {
            "project_id": project_id,
            "document_id": f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "filename": "sample_document.pdf",
            "uploaded_by": get_current_user(request).email,
            "uploaded_at": datetime.now().isoformat()
        }
        
        logger.info(f"Document uploaded to project {project_id}")
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": "Document uploaded successfully"
        })
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error uploading document: {str(e)}"
        }, status_code=500)


@router.post("/{project_id}/flag")
async def flag_project_issue(request: Request, project_id: str):
    """Flag an issue with project"""
    try:
        # Get issue data from request
        data = await request.json()
        issue_description = data.get("issue", "")
        
        if not issue_description:
            raise ValueError("Issue description is required")
        
        # In production, save to database
        # For now, return mock response
        result = {
            "project_id": project_id,
            "issue_id": f"ISSUE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": issue_description,
            "flagged_by": get_current_user(request).email,
            "flagged_at": datetime.now().isoformat()
        }
        
        logger.info(f"Issue flagged for project {project_id}")
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": "Issue flagged successfully"
        })
    except Exception as e:
        logger.error(f"Error flagging issue: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error flagging issue: {str(e)}"
        }, status_code=500)


@router.get("/{project_id}/export")
async def export_project(request: Request, project_id: str, format: str = "json"):
    """Export project data"""
    try:
        # Mock project data for export
        project_data = {
            "project_id": project_id,
            "name": "Organic Honey Sourcing Q1 2024",
            "status": "In Progress",
            "stages": [
                {"stage": 1, "name": "Buyer Request", "status": "Completed"},
                {"stage": 2, "name": "Supplier Search", "status": "Completed"},
                {"stage": 3, "name": "Products in Portfolio", "status": "In Progress"}
            ],
            "exported_at": datetime.now().isoformat()
        }
        
        if format == "json":
            return JSONResponse(content=project_data)
        else:
            # In production, support other formats like CSV, PDF
            return JSONResponse(content={
                "success": False,
                "message": f"Export format '{format}' not supported yet"
            }, status_code=400)
            
    except Exception as e:
        logger.error(f"Error exporting project: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error exporting project: {str(e)}"
        }, status_code=500)


@router.post("/{project_id}/stage/{stage_number}/complete")
async def complete_stage(request: Request, project_id: str, stage_number: int):
    """Mark a stage as completed"""
    try:
        # Validate stage number
        if stage_number < 1 or stage_number > 5:
            raise ValueError("Invalid stage number")
        
        # In production, update in database
        result = {
            "project_id": project_id,
            "stage_number": stage_number,
            "status": "Completed",
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Completed stage {stage_number} for project {project_id}")
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "message": f"Stage {stage_number} marked as completed"
        })
    except Exception as e:
        logger.error(f"Error completing stage: {e}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error completing stage: {str(e)}"
        }, status_code=500)