"""
Cost Monitoring Dashboard for Microsoft Founders Hub
Real-time tracking of Azure service costs
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict
import json
from datetime import datetime

router = APIRouter()

@router.get("/costs", response_class=HTMLResponse)
async def cost_dashboard(request: Request):
    """Display cost monitoring dashboard"""
    
    try:
        from services.cost_tracker import get_cost_tracker
        cost_tracker = get_cost_tracker()
        
        # Get current spend data
        current_spend = cost_tracker.get_current_spend('month')
        daily_spend = cost_tracker.get_current_spend('day')
        
        # Get cost report
        report = cost_tracker.generate_cost_report()
        
        # Format for display
        context = {
            'request': request,
            'month_spend': current_spend,
            'daily_spend': daily_spend,
            'report': report,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return request.app.state.templates.TemplateResponse(
            'admin/cost_dashboard.html',
            context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/costs/current")
async def get_current_costs():
    """API endpoint for current costs"""
    try:
        from services.cost_tracker import get_cost_tracker
        cost_tracker = get_cost_tracker()
        
        return {
            'month': cost_tracker.get_current_spend('month'),
            'day': cost_tracker.get_current_spend('day'),
            'recommendations': cost_tracker.get_optimization_recommendations()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/costs/alert")
async def set_cost_alert(service: str, budget: float):
    """Set cost alert for a service"""
    try:
        from services.cost_tracker import get_cost_tracker
        cost_tracker = get_cost_tracker()
        
        cost_tracker.set_budget_alerts(service, budget)
        
        return {
            'status': 'success',
            'message': f'Budget alert set for {service}: ${budget}/month'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring", response_class=HTMLResponse)
async def monitoring_dashboard(request: Request):
    """Display monitoring dashboard"""
    
    try:
        from services.azure_monitoring import get_monitoring_service
        monitoring = get_monitoring_service()
        
        # Get health metrics
        health = monitoring.get_application_health()
        
        # Get cost analysis for monitoring qualification
        cost_analysis = monitoring.get_cost_analysis(30)
        
        context = {
            'request': request,
            'health': health,
            'cost_analysis': cost_analysis,
            'qualification_status': cost_analysis.get('qualification_status', {}),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return request.app.state.templates.TemplateResponse(
            'admin/monitoring_dashboard.html',
            context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))