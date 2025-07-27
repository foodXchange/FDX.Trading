"""
Planning Mode Service for FoodXchange
Implements strategic planning and task decomposition for complex workflows
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


class PlanStatus(Enum):
    """Status of a plan or task"""
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Types of tasks in the planning system"""
    ANALYSIS = "analysis"
    DATA_EXTRACTION = "data_extraction"
    DECISION = "decision"
    ACTION = "action"
    VALIDATION = "validation"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    MONITORING = "monitoring"


@dataclass
class Task:
    """Individual task within a plan"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.ACTION
    status: PlanStatus = PlanStatus.DRAFT
    dependencies: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    priority: int = 0  # Higher number = higher priority
    estimated_duration: Optional[int] = None  # in seconds
    actual_duration: Optional[int] = None  # in seconds
    
    def can_start(self, completed_tasks: List[str]) -> bool:
        """Check if all dependencies are met"""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "retries": self.retries,
            "priority": self.priority,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration
        }


@dataclass
class Plan:
    """Strategic plan containing multiple tasks"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    goal: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the plan"""
        self.tasks.append(task)
    
    def get_ready_tasks(self, completed_task_ids: List[str]) -> List[Task]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        for task in self.tasks:
            if (task.status == PlanStatus.READY and 
                task.can_start(completed_task_ids)):
                ready_tasks.append(task)
        return sorted(ready_tasks, key=lambda t: t.priority, reverse=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "goal": self.goal,
            "context": self.context,
            "tasks": [task.to_dict() for task in self.tasks],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "success_criteria": self.success_criteria,
            "risk_factors": self.risk_factors
        }


class PlanningService:
    """
    Strategic planning service for complex workflows
    Decomposes goals into actionable tasks with dependencies
    """
    
    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.active_plans: List[str] = []
        self.plan_templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize planning templates for common scenarios"""
        return {
            "rfq_processing": {
                "name": "RFQ Processing Plan",
                "description": "Complete workflow for processing a Request for Quote",
                "tasks": [
                    {
                        "name": "Analyze RFQ Requirements",
                        "task_type": TaskType.ANALYSIS,
                        "description": "Extract and analyze all requirements from the RFQ",
                        "estimated_duration": 60
                    },
                    {
                        "name": "Identify Matching Suppliers",
                        "task_type": TaskType.DATA_EXTRACTION,
                        "description": "Find suppliers that can fulfill the requirements",
                        "dependencies": ["Analyze RFQ Requirements"],
                        "estimated_duration": 120
                    },
                    {
                        "name": "Generate Quote Requests",
                        "task_type": TaskType.ACTION,
                        "description": "Create and send quote requests to suppliers",
                        "dependencies": ["Identify Matching Suppliers"],
                        "estimated_duration": 180
                    },
                    {
                        "name": "Collect Supplier Responses",
                        "task_type": TaskType.MONITORING,
                        "description": "Monitor and collect responses from suppliers",
                        "dependencies": ["Generate Quote Requests"],
                        "estimated_duration": 3600
                    },
                    {
                        "name": "Compare Quotes",
                        "task_type": TaskType.ANALYSIS,
                        "description": "Analyze and compare received quotes",
                        "dependencies": ["Collect Supplier Responses"],
                        "estimated_duration": 300
                    },
                    {
                        "name": "Generate Recommendation",
                        "task_type": TaskType.DECISION,
                        "description": "Create recommendation based on analysis",
                        "dependencies": ["Compare Quotes"],
                        "estimated_duration": 180
                    }
                ]
            },
            "email_intelligence": {
                "name": "Email Intelligence Processing",
                "description": "Comprehensive email analysis and action workflow",
                "tasks": [
                    {
                        "name": "Email Classification",
                        "task_type": TaskType.ANALYSIS,
                        "description": "Classify email type and intent",
                        "estimated_duration": 30
                    },
                    {
                        "name": "Extract Key Information",
                        "task_type": TaskType.DATA_EXTRACTION,
                        "description": "Extract prices, dates, products, and other data",
                        "dependencies": ["Email Classification"],
                        "estimated_duration": 60
                    },
                    {
                        "name": "Match to Existing Data",
                        "task_type": TaskType.INTEGRATION,
                        "description": "Match email data to existing RFQs, orders, or suppliers",
                        "dependencies": ["Extract Key Information"],
                        "estimated_duration": 90
                    },
                    {
                        "name": "Determine Actions",
                        "task_type": TaskType.DECISION,
                        "description": "Decide what actions to take based on email content",
                        "dependencies": ["Match to Existing Data"],
                        "estimated_duration": 45
                    },
                    {
                        "name": "Execute Actions",
                        "task_type": TaskType.ACTION,
                        "description": "Execute determined actions",
                        "dependencies": ["Determine Actions"],
                        "estimated_duration": 120
                    },
                    {
                        "name": "Send Notifications",
                        "task_type": TaskType.NOTIFICATION,
                        "description": "Notify relevant parties of actions taken",
                        "dependencies": ["Execute Actions"],
                        "estimated_duration": 30
                    }
                ]
            },
            "supplier_onboarding": {
                "name": "Supplier Onboarding",
                "description": "Complete workflow for onboarding a new supplier",
                "tasks": [
                    {
                        "name": "Collect Supplier Information",
                        "task_type": TaskType.DATA_EXTRACTION,
                        "description": "Gather all required supplier information",
                        "estimated_duration": 300
                    },
                    {
                        "name": "Verify Credentials",
                        "task_type": TaskType.VALIDATION,
                        "description": "Verify supplier credentials and certifications",
                        "dependencies": ["Collect Supplier Information"],
                        "estimated_duration": 600
                    },
                    {
                        "name": "Assess Capabilities",
                        "task_type": TaskType.ANALYSIS,
                        "description": "Analyze supplier capabilities and product range",
                        "dependencies": ["Collect Supplier Information"],
                        "estimated_duration": 450
                    },
                    {
                        "name": "Setup in System",
                        "task_type": TaskType.ACTION,
                        "description": "Create supplier profile in the system",
                        "dependencies": ["Verify Credentials", "Assess Capabilities"],
                        "estimated_duration": 180
                    },
                    {
                        "name": "Configure Integration",
                        "task_type": TaskType.INTEGRATION,
                        "description": "Setup email and API integrations",
                        "dependencies": ["Setup in System"],
                        "estimated_duration": 300
                    },
                    {
                        "name": "Send Welcome Package",
                        "task_type": TaskType.NOTIFICATION,
                        "description": "Send onboarding materials to supplier",
                        "dependencies": ["Configure Integration"],
                        "estimated_duration": 60
                    }
                ]
            }
        }
    
    async def create_plan(self, goal: str, context: Dict[str, Any], 
                         template: Optional[str] = None) -> Plan:
        """Create a new strategic plan"""
        plan = Plan(
            name=f"Plan for: {goal[:50]}",
            goal=goal,
            context=context
        )
        
        if template and template in self.plan_templates:
            # Use template as starting point
            template_data = self.plan_templates[template]
            plan.name = template_data["name"]
            plan.description = template_data["description"]
            
            # Create tasks from template
            task_id_map = {}
            for task_template in template_data["tasks"]:
                task = Task(
                    name=task_template["name"],
                    description=task_template["description"],
                    task_type=task_template["task_type"],
                    estimated_duration=task_template.get("estimated_duration"),
                    status=PlanStatus.READY
                )
                task_id_map[task.name] = task.id
                plan.add_task(task)
            
            # Map dependencies
            for i, task_template in enumerate(template_data["tasks"]):
                if "dependencies" in task_template:
                    task = plan.tasks[i]
                    task.dependencies = [
                        task_id_map[dep_name] 
                        for dep_name in task_template["dependencies"]
                    ]
        else:
            # Create custom plan based on goal analysis
            plan = await self._analyze_and_plan(goal, context)
        
        self.plans[plan.id] = plan
        logger.info(f"Created plan {plan.id} with {len(plan.tasks)} tasks")
        return plan
    
    async def _analyze_and_plan(self, goal: str, context: Dict[str, Any]) -> Plan:
        """Analyze goal and create custom plan"""
        plan = Plan(
            name=f"Custom Plan: {goal[:50]}",
            description=f"Automated plan for achieving: {goal}",
            goal=goal,
            context=context
        )
        
        # Analyze goal to determine task types needed
        goal_lower = goal.lower()
        
        # Start with analysis task
        analysis_task = Task(
            name="Initial Analysis",
            description="Analyze the goal and current state",
            task_type=TaskType.ANALYSIS,
            status=PlanStatus.READY,
            priority=10,
            estimated_duration=120
        )
        plan.add_task(analysis_task)
        
        # Add task types based on goal keywords
        if any(word in goal_lower for word in ["compare", "analyze", "evaluate"]):
            plan.add_task(Task(
                name="Data Collection",
                description="Collect relevant data for analysis",
                task_type=TaskType.DATA_EXTRACTION,
                dependencies=[analysis_task.id],
                status=PlanStatus.READY,
                priority=8,
                estimated_duration=300
            ))
        
        if any(word in goal_lower for word in ["decide", "choose", "select"]):
            plan.add_task(Task(
                name="Decision Making",
                description="Make decision based on available data",
                task_type=TaskType.DECISION,
                dependencies=[analysis_task.id],
                status=PlanStatus.READY,
                priority=7,
                estimated_duration=180
            ))
        
        if any(word in goal_lower for word in ["implement", "create", "build", "send"]):
            plan.add_task(Task(
                name="Implementation",
                description="Implement the required actions",
                task_type=TaskType.ACTION,
                dependencies=[analysis_task.id],
                status=PlanStatus.READY,
                priority=6,
                estimated_duration=600
            ))
        
        # Always add validation and notification
        validation_task = Task(
            name="Validate Results",
            description="Validate that goal has been achieved",
            task_type=TaskType.VALIDATION,
            dependencies=[t.id for t in plan.tasks[1:]],  # Depends on all other tasks
            status=PlanStatus.READY,
            priority=3,
            estimated_duration=120
        )
        plan.add_task(validation_task)
        
        plan.add_task(Task(
            name="Final Report",
            description="Generate report on plan execution",
            task_type=TaskType.NOTIFICATION,
            dependencies=[validation_task.id],
            status=PlanStatus.READY,
            priority=1,
            estimated_duration=60
        ))
        
        return plan
    
    async def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute a plan asynchronously"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        if plan.status == PlanStatus.IN_PROGRESS:
            raise ValueError(f"Plan {plan_id} is already in progress")
        
        plan.status = PlanStatus.IN_PROGRESS
        plan.started_at = datetime.utcnow()
        self.active_plans.append(plan_id)
        
        completed_tasks = []
        failed_tasks = []
        
        try:
            while True:
                # Get ready tasks
                ready_tasks = plan.get_ready_tasks([t.id for t in completed_tasks])
                
                if not ready_tasks:
                    # Check if all tasks are complete
                    incomplete_tasks = [
                        t for t in plan.tasks 
                        if t.status not in [PlanStatus.COMPLETED, PlanStatus.FAILED]
                    ]
                    if not incomplete_tasks:
                        break
                    
                    # Check for blocked tasks
                    blocked_tasks = [
                        t for t in incomplete_tasks
                        if not t.can_start([ct.id for ct in completed_tasks])
                    ]
                    if blocked_tasks:
                        logger.warning(f"Plan {plan_id} has blocked tasks")
                        plan.status = PlanStatus.BLOCKED
                        break
                    
                    # Wait for tasks to complete
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks (potentially in parallel)
                task_results = await asyncio.gather(
                    *[self._execute_task(task, plan.context) for task in ready_tasks],
                    return_exceptions=True
                )
                
                # Process results
                for task, result in zip(ready_tasks, task_results):
                    if isinstance(result, Exception):
                        task.status = PlanStatus.FAILED
                        task.error = str(result)
                        failed_tasks.append(task)
                        logger.error(f"Task {task.name} failed: {result}")
                    else:
                        task.status = PlanStatus.COMPLETED
                        task.outputs = result
                        completed_tasks.append(task)
                        logger.info(f"Task {task.name} completed successfully")
            
            # Determine final plan status
            if failed_tasks:
                plan.status = PlanStatus.FAILED
            elif plan.status != PlanStatus.BLOCKED:
                plan.status = PlanStatus.COMPLETED
            
            plan.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Plan {plan_id} execution failed: {str(e)}")
            plan.status = PlanStatus.FAILED
            plan.completed_at = datetime.utcnow()
        finally:
            self.active_plans.remove(plan_id)
        
        return {
            "plan_id": plan_id,
            "status": plan.status.value,
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "total_tasks": len(plan.tasks),
            "duration": (plan.completed_at - plan.started_at).total_seconds() if plan.completed_at else None
        }
    
    async def _execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an individual task"""
        task.status = PlanStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        
        try:
            # Task execution logic based on type
            if task.task_type == TaskType.ANALYSIS:
                result = await self._execute_analysis_task(task, context)
            elif task.task_type == TaskType.DATA_EXTRACTION:
                result = await self._execute_extraction_task(task, context)
            elif task.task_type == TaskType.DECISION:
                result = await self._execute_decision_task(task, context)
            elif task.task_type == TaskType.ACTION:
                result = await self._execute_action_task(task, context)
            elif task.task_type == TaskType.VALIDATION:
                result = await self._execute_validation_task(task, context)
            elif task.task_type == TaskType.NOTIFICATION:
                result = await self._execute_notification_task(task, context)
            elif task.task_type == TaskType.INTEGRATION:
                result = await self._execute_integration_task(task, context)
            elif task.task_type == TaskType.MONITORING:
                result = await self._execute_monitoring_task(task, context)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            task.completed_at = datetime.utcnow()
            task.actual_duration = (task.completed_at - task.started_at).total_seconds()
            
            return result
            
        except Exception as e:
            task.retries += 1
            if task.retries < task.max_retries:
                # Retry logic
                await asyncio.sleep(2 ** task.retries)  # Exponential backoff
                return await self._execute_task(task, context)
            else:
                raise e
    
    async def _execute_analysis_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis task"""
        # Simulate analysis
        await asyncio.sleep(1)
        return {
            "analysis_complete": True,
            "findings": ["Finding 1", "Finding 2", "Finding 3"],
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }
    
    async def _execute_extraction_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data extraction task"""
        # Simulate extraction
        await asyncio.sleep(1)
        return {
            "extracted_data": {
                "items": ["Item 1", "Item 2"],
                "values": [100, 200],
                "metadata": {"source": "simulation"}
            }
        }
    
    async def _execute_decision_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decision task"""
        # Simulate decision making
        await asyncio.sleep(1)
        return {
            "decision": "approved",
            "confidence": 0.85,
            "reasoning": "Based on analysis results"
        }
    
    async def _execute_action_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action task"""
        # Simulate action
        await asyncio.sleep(2)
        return {
            "action_taken": True,
            "result": "success",
            "details": {"affected_items": 5}
        }
    
    async def _execute_validation_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation task"""
        # Simulate validation
        await asyncio.sleep(1)
        return {
            "validation_passed": True,
            "checks_performed": 10,
            "issues_found": 0
        }
    
    async def _execute_notification_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification task"""
        # Simulate notification
        await asyncio.sleep(0.5)
        return {
            "notifications_sent": 3,
            "recipients": ["user1", "user2", "admin"]
        }
    
    async def _execute_integration_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration task"""
        # Simulate integration
        await asyncio.sleep(1.5)
        return {
            "integration_complete": True,
            "systems_connected": 2,
            "data_synced": True
        }
    
    async def _execute_monitoring_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        # Simulate monitoring
        await asyncio.sleep(3)
        return {
            "monitoring_complete": True,
            "events_captured": 15,
            "alerts_generated": 2
        }
    
    def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """Get current status of a plan"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        completed_tasks = [t for t in plan.tasks if t.status == PlanStatus.COMPLETED]
        failed_tasks = [t for t in plan.tasks if t.status == PlanStatus.FAILED]
        in_progress_tasks = [t for t in plan.tasks if t.status == PlanStatus.IN_PROGRESS]
        
        return {
            "plan": plan.to_dict(),
            "summary": {
                "total_tasks": len(plan.tasks),
                "completed": len(completed_tasks),
                "failed": len(failed_tasks),
                "in_progress": len(in_progress_tasks),
                "progress_percentage": (len(completed_tasks) / len(plan.tasks) * 100) if plan.tasks else 0
            }
        }
    
    def get_active_plans(self) -> List[Dict[str, Any]]:
        """Get all active plans"""
        active_plans = []
        for plan_id in self.active_plans:
            try:
                status = self.get_plan_status(plan_id)
                active_plans.append(status)
            except Exception as e:
                logger.error(f"Error getting status for plan {plan_id}: {str(e)}")
        
        return active_plans


# Singleton instance
planning_service = PlanningService()