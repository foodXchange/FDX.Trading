"""
API Routes for Agent Management
Provides endpoints to control and monitor the email monitoring agent
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
import asyncio

from app.database import get_db
from app.agents import agent_manager, AgentState
from app.models.user import User
from app.auth import get_current_user

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/status")
async def get_all_agents_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get status of all agents"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    return {
        "agents": agent_manager.get_all_status(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/email-monitor/start")
async def start_email_monitor_agent(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start the email monitoring agent"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    agent_id = "email_monitor_main"
    
    try:
        # Check if agent already exists
        if agent_id in agent_manager.agents:
            agent = agent_manager.agents[agent_id]
            if agent.is_running:
                return {
                    "status": "already_running",
                    "message": "Email monitor agent is already running",
                    "agent_status": agent.get_status()
                }
        else:
            # Create new agent
            agent = await agent_manager.create_agent(agent_id, db)
            
        # Start agent in background
        background_tasks.add_task(agent_manager.start_agent, agent_id)
        
        return {
            "status": "started",
            "message": "Email monitor agent started successfully",
            "agent_id": agent_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")


@router.post("/email-monitor/stop")
async def stop_email_monitor_agent(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Stop the email monitoring agent"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    agent_id = "email_monitor_main"
    
    try:
        await agent_manager.stop_agent(agent_id)
        
        return {
            "status": "stopped",
            "message": "Email monitor agent stopped successfully",
            "agent_id": agent_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")


@router.get("/email-monitor/status")
async def get_email_monitor_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get status of the email monitoring agent"""
    agent_id = "email_monitor_main"
    
    if agent_id not in agent_manager.agents:
        return {
            "status": "not_created",
            "message": "Email monitor agent not initialized"
        }
        
    agent = agent_manager.agents[agent_id]
    return agent.get_status()


@router.post("/email-monitor/configure")
async def configure_email_monitor(
    config: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Configure the email monitoring agent"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    agent_id = "email_monitor_main"
    
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    agent = agent_manager.agents[agent_id]
    
    # Update configuration
    if "loop_interval" in config:
        agent.loop_interval = config["loop_interval"]
    if "max_emails_per_cycle" in config:
        agent.max_emails_per_cycle = config["max_emails_per_cycle"]
    if "confidence_threshold" in config:
        agent.confidence_threshold = config["confidence_threshold"]
        
    return {
        "status": "configured",
        "message": "Agent configuration updated",
        "config": {
            "loop_interval": agent.loop_interval,
            "max_emails_per_cycle": agent.max_emails_per_cycle,
            "confidence_threshold": agent.confidence_threshold
        }
    }


@router.post("/email-monitor/run-once")
async def run_email_monitor_once(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Run the email monitor agent once (without loop)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    agent_id = "email_monitor_single_run"
    
    try:
        # Create temporary agent for single run
        agent = await agent_manager.create_agent(agent_id, db)
        
        # Run one cycle
        async def run_single_cycle():
            await agent._run_cycle()
            # Clean up temporary agent
            del agent_manager.agents[agent_id]
            
        background_tasks.add_task(run_single_cycle)
        
        return {
            "status": "running",
            "message": "Email monitor agent running single cycle",
            "agent_id": agent_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run agent: {str(e)}")


@router.get("/email-monitor/metrics")
async def get_email_monitor_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed metrics from the email monitoring agent"""
    agent_id = "email_monitor_main"
    
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    agent = agent_manager.agents[agent_id]
    metrics = agent.metrics
    
    return {
        "metrics": metrics.to_dict(),
        "performance": {
            "avg_processing_time": metrics.total_runtime_seconds / max(metrics.total_emails_processed, 1),
            "success_rate": metrics.successful_updates / max(metrics.total_emails_processed, 1) * 100 if metrics.total_emails_processed > 0 else 0,
            "error_rate": metrics.failed_updates / max(metrics.total_emails_processed, 1) * 100 if metrics.total_emails_processed > 0 else 0
        },
        "health": {
            "is_healthy": agent.state != AgentState.ERROR,
            "consecutive_errors": metrics.error_count,
            "last_error_threshold": 5  # Alert if more than 5 consecutive errors
        }
    }


@router.get("/email-monitor/logs")
async def get_email_monitor_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get recent logs from the email monitoring agent"""
    agent_id = "email_monitor_main"
    
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    agent = agent_manager.agents[agent_id]
    
    # Get state history (recent state transitions)
    state_history = agent._state_history[-limit:]
    
    return {
        "logs": state_history,
        "total_transitions": len(agent._state_history),
        "current_state": agent.state.value
    }


@router.post("/test/email-processing")
async def test_email_processing(
    email_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test email processing pipeline without running full agent"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    # Import services
    from app.services.ai_service import analyze_email_with_ai
    from app.agents.email_monitor_agent import SupplierEmailMonitorAgent
    
    try:
        # Create temporary agent
        agent = SupplierEmailMonitorAgent(db)
        
        # Test AI analysis
        ai_analysis = await analyze_email_with_ai(email_data)
        
        # Create mock email object
        class MockEmail:
            def __init__(self, data):
                self.id = data.get("id", "test_123")
                self.subject = data.get("subject", "Test Email")
                self.sender_email = data.get("sender", "test@supplier.com")
                self.body = data.get("body", "Test email body")
                
        mock_email = MockEmail(email_data)
        
        # Test single email processing
        result = await agent._analyze_single_email(mock_email)
        
        return {
            "status": "success",
            "ai_analysis": ai_analysis,
            "processing_result": {
                "email_id": result.email_id,
                "supplier_id": result.supplier_id,
                "intent": result.intent.value,
                "confidence": result.confidence,
                "extracted_data": result.extracted_data
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


# Include router in main app
def include_agent_routes(app):
    """Include agent routes in the main FastAPI app"""
    app.include_router(router)