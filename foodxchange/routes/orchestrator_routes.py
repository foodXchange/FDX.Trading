"""
Routes for One-Person Company Orchestrator
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user, get_current_user_context
from app.models.user import User
from app.agents.one_person_orchestrator import (
    get_or_create_orchestrator, 
    TaskType, 
    TaskStatus
)

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/status")
async def get_orchestrator_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current status of the user's orchestrator"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    return orchestrator.get_status()


@router.post("/start")
async def start_orchestrator(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start the automation orchestrator"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    if orchestrator.is_running:
        return {
            "status": "already_running",
            "message": "Orchestrator is already running"
        }
    
    background_tasks.add_task(orchestrator.start)
    
    return {
        "status": "started",
        "message": "Orchestrator started successfully"
    }


@router.post("/stop")
async def stop_orchestrator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Stop the automation orchestrator"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    if not orchestrator.is_running:
        return {
            "status": "not_running",
            "message": "Orchestrator is not running"
        }
    
    await orchestrator.stop()
    
    return {
        "status": "stopped",
        "message": "Orchestrator stopped successfully"
    }


@router.get("/tasks")
async def get_task_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get task execution history"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    return {
        "tasks": orchestrator.get_task_history(limit),
        "total_tasks": len(orchestrator.tasks)
    }


@router.post("/tasks")
async def create_manual_task(
    task_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a manual task"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    try:
        task_type = TaskType(task_data["type"])
        config = task_data.get("config", {})
        
        task = await orchestrator.create_task(task_type, config)
        
        return {
            "status": "created",
            "task_id": task.id,
            "message": f"Task {task_type.value} created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/schedule")
async def get_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the daily automation schedule"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    return {
        "schedule": orchestrator.daily_schedule,
        "timezone": "UTC"  # TODO: Add user timezone support
    }


@router.put("/schedule")
async def update_schedule(
    schedule_data: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update the daily automation schedule"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    # Validate schedule
    for item in schedule_data:
        if "time" not in item or "task" not in item:
            raise HTTPException(status_code=400, detail="Invalid schedule format")
        
        try:
            TaskType(item["task"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {item['task']}")
    
    orchestrator.daily_schedule = schedule_data
    
    return {
        "status": "updated",
        "message": "Schedule updated successfully"
    }


@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed automation metrics"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    metrics = orchestrator.metrics
    
    return {
        "metrics": {
            "tasks_created": metrics.tasks_created,
            "tasks_completed": metrics.tasks_completed,
            "tasks_failed": metrics.tasks_failed,
            "emails_processed": metrics.emails_processed,
            "rfqs_created": metrics.rfqs_created,
            "quotes_analyzed": metrics.quotes_analyzed,
            "suppliers_discovered": metrics.suppliers_discovered,
            "time_saved_hours": metrics.total_time_saved_hours,
            "last_run": metrics.last_run.isoformat() if metrics.last_run else None
        },
        "efficiency": {
            "success_rate": (metrics.tasks_completed / max(metrics.tasks_created, 1)) * 100,
            "automation_value": f"${metrics.total_time_saved_hours * 50:.2f}",  # $50/hour estimate
            "daily_capacity": "Handling work of 3-4 employees"
        }
    }


# Quick action endpoints for common tasks
@router.post("/quick/email-check")
async def quick_email_check(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Quick action to check emails now"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    task = await orchestrator.create_task(
        TaskType.EMAIL_MONITORING,
        {"process_unread": True, "max_emails": 20}
    )
    
    return {
        "status": "scheduled",
        "task_id": task.id,
        "message": "Email check scheduled"
    }


@router.post("/quick/find-suppliers")
async def quick_find_suppliers(
    category: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Quick action to find suppliers for a category"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    task = await orchestrator.create_task(
        TaskType.SUPPLIER_DISCOVERY,
        {"categories": [category], "max_suppliers": 3}
    )
    
    return {
        "status": "scheduled",
        "task_id": task.id,
        "message": f"Supplier search for '{category}' scheduled"
    }


@router.post("/quick/daily-report")
async def quick_daily_report(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Quick action to generate daily report"""
    orchestrator = await get_or_create_orchestrator(current_user, db)
    
    task = await orchestrator.create_task(
        TaskType.REPORT_GENERATION,
        {"type": "daily_summary", "send_email": True}
    )
    
    return {
        "status": "scheduled",
        "task_id": task.id,
        "message": "Daily report generation scheduled"
    }


def include_orchestrator_routes(app):
    """Include orchestrator routes in the main app"""
    app.include_router(router)