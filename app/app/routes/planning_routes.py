"""
Planning and Agent Routes
Handles planning mode and agent orchestration functionality
"""
from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user_context
from app.services.planning_service import planning_service, PlanStatus
from app.services.agent_service import agent_orchestrator
from app.services.email_ai_service import email_ai_service
from app.models.email import Email

templates = Jinja2Templates(directory="app/templates")

def include_planning_routes(app):
    """Include planning and agent-related routes in the main app"""
    
    # Initialize agent team on startup
    agent_orchestrator.initialize_default_team()
    
    @app.get("/planning", response_class=HTMLResponse, name="planning_dashboard")
    async def planning_dashboard(request: Request, db: Session = Depends(get_db)):
        user = get_current_user_context(request, db)
        if not user:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/login", status_code=302)
        
        # Get active plans
        active_plans = planning_service.get_active_plans()
        
        # Get agent status
        agent_status = agent_orchestrator.get_agent_status()
        
        # Get plan templates
        templates_list = [
            {
                "id": "rfq_processing",
                "name": "RFQ Processing",
                "description": "Complete workflow for processing a Request for Quote"
            },
            {
                "id": "email_intelligence",
                "name": "Email Intelligence",
                "description": "Comprehensive email analysis and action workflow"
            },
            {
                "id": "supplier_onboarding",
                "name": "Supplier Onboarding",
                "description": "Complete workflow for onboarding a new supplier"
            }
        ]
        
        return templates.TemplateResponse("planning_dashboard.html", {
            "request": request,
            "active_plans": active_plans,
            "agent_status": agent_status,
            "plan_templates": templates_list,
            "current_user": user
        })
    
    @app.post("/api/planning/create", response_class=JSONResponse)
    async def create_plan(request: Request, db: Session = Depends(get_db)):
        """Create a new plan"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        body = await request.json()
        goal = body.get("goal", "")
        context = body.get("context", {})
        template = body.get("template")
        
        try:
            # Create plan
            plan = await planning_service.create_plan(goal, context, template)
            
            return {
                "plan_id": plan.id,
                "plan": plan.to_dict(),
                "message": f"Created plan with {len(plan.tasks)} tasks"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")
    
    @app.post("/api/planning/execute/{plan_id}", response_class=JSONResponse)
    async def execute_plan(plan_id: str, request: Request, 
                          background_tasks: BackgroundTasks, 
                          db: Session = Depends(get_db)):
        """Execute a plan"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        try:
            # Start plan execution in background
            background_tasks.add_task(planning_service.execute_plan, plan_id)
            
            return {
                "status": "started",
                "message": f"Plan {plan_id} execution started",
                "plan_id": plan_id
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to execute plan: {str(e)}")
    
    @app.get("/api/planning/status/{plan_id}", response_class=JSONResponse)
    async def get_plan_status(plan_id: str, request: Request, db: Session = Depends(get_db)):
        """Get status of a plan"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        try:
            status = planning_service.get_plan_status(plan_id)
            return status
            
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get plan status: {str(e)}")
    
    @app.post("/api/agents/process", response_class=JSONResponse)
    async def process_with_agents(request: Request, db: Session = Depends(get_db)):
        """Process a request using the agent system"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        body = await request.json()
        user_request = body.get("request", "")
        context = body.get("context", {})
        
        try:
            # Process request with agents
            result = await agent_orchestrator.process_request(user_request, context)
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")
    
    @app.get("/api/agents/status", response_class=JSONResponse)
    async def get_agents_status(request: Request, db: Session = Depends(get_db)):
        """Get status of all agents"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        return agent_orchestrator.get_agent_status()
    
    @app.post("/api/planning/email-workflow", response_class=JSONResponse)
    async def create_email_workflow(request: Request, db: Session = Depends(get_db)):
        """Create a workflow for processing emails"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        body = await request.json()
        email_ids = body.get("email_ids", [])
        
        if not email_ids:
            # Get unprocessed emails
            emails = db.query(Email).filter(
                Email.processed == False,
                Email.email_type == 'supplier'
            ).limit(10).all()
            email_ids = [e.id for e in emails]
        
        try:
            # Create plan for email processing
            plan = await planning_service.create_plan(
                goal=f"Process {len(email_ids)} supplier emails",
                context={"email_ids": email_ids},
                template="email_intelligence"
            )
            
            # Execute plan
            result = await planning_service.execute_plan(plan.id)
            
            return {
                "plan_id": plan.id,
                "emails_processed": len(email_ids),
                "result": result
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Email workflow failed: {str(e)}")
    
    @app.post("/api/planning/autonomous-mode", response_class=JSONResponse)
    async def toggle_autonomous_mode(request: Request, 
                                   background_tasks: BackgroundTasks,
                                   db: Session = Depends(get_db)):
        """Toggle autonomous processing mode"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        body = await request.json()
        enable = body.get("enable", False)
        max_iterations = body.get("max_iterations", 10)
        
        if enable:
            # Start autonomous loop in background
            background_tasks.add_task(
                agent_orchestrator.autonomous_loop, 
                max_iterations
            )
            
            return {
                "status": "enabled",
                "message": f"Autonomous mode enabled for {max_iterations} iterations"
            }
        else:
            return {
                "status": "disabled",
                "message": "Autonomous mode disabled"
            }
    
    @app.get("/api/planning/templates/{template_id}", response_class=JSONResponse)
    async def get_plan_template(template_id: str, request: Request, db: Session = Depends(get_db)):
        """Get details of a plan template"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        if template_id in planning_service.plan_templates:
            template = planning_service.plan_templates[template_id]
            return {
                "template_id": template_id,
                "template": template
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    
    @app.post("/api/planning/optimize/{plan_id}", response_class=JSONResponse)
    async def optimize_plan(plan_id: str, request: Request, db: Session = Depends(get_db)):
        """Optimize an existing plan"""
        user = get_current_user_context(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        try:
            # Get plan
            plan_status = planning_service.get_plan_status(plan_id)
            plan = plan_status["plan"]
            
            # Use planner agent to optimize
            if "planner-001" in agent_orchestrator.agents:
                planner = agent_orchestrator.agents["planner-001"]
                optimization = await planner.think(
                    f"Optimize this plan for efficiency: {json.dumps(plan)}",
                    {"plan": plan}
                )
                
                return {
                    "plan_id": plan_id,
                    "optimization_suggestions": optimization
                }
            else:
                raise HTTPException(status_code=500, detail="Planner agent not available")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to optimize plan: {str(e)}")