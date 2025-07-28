"""
Infinite Agentic Coding Service for FoodXchange
Implements autonomous agents that can plan, execute, and iterate on tasks
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Type
from enum import Enum
from dataclasses import dataclass, field
import uuid
from abc import ABC, abstractmethod

from foodxchange.services.planning_service import PlanningService, Plan, Task, TaskType, PlanStatus
from foodxchange.services.email_ai_service import EmailAIService
from foodxchange.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Roles that agents can take"""
    PLANNER = "planner"
    ANALYZER = "analyzer"
    EXECUTOR = "executor"
    VALIDATOR = "validator"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"


class AgentCapability(Enum):
    """Capabilities that agents can have"""
    EMAIL_ANALYSIS = "email_analysis"
    DATA_EXTRACTION = "data_extraction"
    SUPPLIER_MANAGEMENT = "supplier_management"
    QUOTE_PROCESSING = "quote_processing"
    DECISION_MAKING = "decision_making"
    REPORT_GENERATION = "report_generation"
    WORKFLOW_AUTOMATION = "workflow_automation"
    SYSTEM_INTEGRATION = "system_integration"


@dataclass
class AgentMemory:
    """Memory system for agents to maintain context"""
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term: Dict[str, Any] = field(default_factory=dict)
    working_memory: List[Dict[str, Any]] = field(default_factory=list)
    max_working_memory: int = 10
    
    def add_to_working_memory(self, item: Dict[str, Any]) -> None:
        """Add item to working memory with FIFO management"""
        self.working_memory.append(item)
        if len(self.working_memory) > self.max_working_memory:
            self.working_memory.pop(0)
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context from memory"""
        return {
            "short_term": self.short_term,
            "recent_actions": self.working_memory[-5:] if self.working_memory else [],
            "long_term_keys": list(self.long_term.keys())
        }


@dataclass
class AgentMessage:
    """Message passed between agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    message_type: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    requires_response: bool = False
    priority: int = 0


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, name: str, role: AgentRole, 
                 capabilities: List[AgentCapability]):
        self.id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.memory = AgentMemory()
        self.status = "idle"
        self.current_task: Optional[Task] = None
        self.message_queue: List[AgentMessage] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_task_time": 0,
            "success_rate": 0
        }
    
    @abstractmethod
    async def process_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming message - must be implemented by subclasses"""
        pass
    
    async def think(self, prompt: str, context: Dict[str, Any]) -> str:
        """Use AI to think about a problem"""
        memory_context = self.memory.get_context()
        full_context = {
            **context,
            "agent_role": self.role.value,
            "agent_capabilities": [cap.value for cap in self.capabilities],
            "memory": memory_context
        }
        
        response = await ai_service.get_completion(
            prompt=f"As a {self.role.value} agent with capabilities in {', '.join([cap.value for cap in self.capabilities])}, {prompt}",
            context=json.dumps(full_context)
        )
        
        # Store thought in working memory
        self.memory.add_to_working_memory({
            "type": "thought",
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return response
    
    def update_metrics(self, success: bool, duration: float) -> None:
        """Update performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
        
        total_tasks = (self.performance_metrics["tasks_completed"] + 
                      self.performance_metrics["tasks_failed"])
        
        # Update average task time
        current_avg = self.performance_metrics["average_task_time"]
        self.performance_metrics["average_task_time"] = (
            (current_avg * (total_tasks - 1) + duration) / total_tasks
        )
        
        # Update success rate
        self.performance_metrics["success_rate"] = (
            self.performance_metrics["tasks_completed"] / total_tasks
        )


class PlannerAgent(BaseAgent):
    """Agent specialized in creating and optimizing plans"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Strategic Planner",
            role=AgentRole.PLANNER,
            capabilities=[
                AgentCapability.WORKFLOW_AUTOMATION,
                AgentCapability.DECISION_MAKING
            ]
        )
        self.planning_service = PlanningService()
    
    async def process_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plan based on the task"""
        start_time = datetime.utcnow()
        
        try:
            # Analyze the task to determine planning approach
            analysis = await self.think(
                f"Analyze this task and determine the best planning approach: {task.description}",
                context
            )
            
            # Create plan based on analysis
            plan = await self.planning_service.create_plan(
                goal=task.description,
                context={**context, "analysis": analysis},
                template=self._determine_template(task, analysis)
            )
            
            # Optimize plan based on context
            optimized_plan = await self._optimize_plan(plan, context)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(True, duration)
            
            return {
                "plan_id": optimized_plan.id,
                "plan_summary": {
                    "total_tasks": len(optimized_plan.tasks),
                    "estimated_duration": sum(t.estimated_duration or 0 for t in optimized_plan.tasks),
                    "task_types": list(set(t.task_type.value for t in optimized_plan.tasks))
                }
            }
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(False, duration)
            logger.error(f"PlannerAgent failed: {str(e)}")
            raise
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle planning-related messages"""
        if message.message_type == "plan_request":
            # Create a plan based on the request
            plan = await self.planning_service.create_plan(
                goal=message.content.get("goal", ""),
                context=message.content.get("context", {})
            )
            
            return AgentMessage(
                sender=self.id,
                recipient=message.sender,
                message_type="plan_response",
                content={"plan": plan.to_dict()},
                requires_response=False
            )
        
        return None
    
    def _determine_template(self, task: Task, analysis: str) -> Optional[str]:
        """Determine which template to use based on task and analysis"""
        task_desc_lower = task.description.lower()
        
        if "rfq" in task_desc_lower or "quote" in task_desc_lower:
            return "rfq_processing"
        elif "email" in task_desc_lower:
            return "email_intelligence"
        elif "supplier" in task_desc_lower and "onboard" in task_desc_lower:
            return "supplier_onboarding"
        
        return None
    
    async def _optimize_plan(self, plan: Plan, context: Dict[str, Any]) -> Plan:
        """Optimize plan based on context and constraints"""
        # Analyze dependencies and optimize task order
        optimization_thoughts = await self.think(
            f"Optimize this plan for efficiency: {plan.name} with {len(plan.tasks)} tasks",
            {"plan": plan.to_dict(), "context": context}
        )
        
        # In a real implementation, this would modify the plan based on AI insights
        # For now, we'll just return the plan as-is
        return plan


class AnalyzerAgent(BaseAgent):
    """Agent specialized in analyzing data and extracting insights"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Data Analyzer",
            role=AgentRole.ANALYZER,
            capabilities=[
                AgentCapability.EMAIL_ANALYSIS,
                AgentCapability.DATA_EXTRACTION,
                AgentCapability.REPORT_GENERATION
            ]
        )
        self.email_service = EmailAIService()
    
    async def process_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data based on task requirements"""
        start_time = datetime.utcnow()
        
        try:
            if task.task_type == TaskType.ANALYSIS:
                if "email" in context:
                    # Analyze email
                    result = await self.email_service.analyze_email(
                        context["email"].get("content", ""),
                        context["email"].get("subject", ""),
                        context["email"].get("sender", "")
                    )
                else:
                    # General analysis
                    analysis = await self.think(
                        f"Analyze the following data: {json.dumps(context.get('data', {}))}",
                        context
                    )
                    result = {"analysis": analysis}
            
            elif task.task_type == TaskType.DATA_EXTRACTION:
                # Extract data based on requirements
                extraction_prompt = f"Extract {task.inputs.get('extract_type', 'relevant data')} from: {json.dumps(context.get('data', {}))}"
                extracted = await self.think(extraction_prompt, context)
                result = {"extracted_data": extracted}
            
            else:
                result = {"error": f"Unsupported task type for analyzer: {task.task_type}"}
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(True, duration)
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(False, duration)
            logger.error(f"AnalyzerAgent failed: {str(e)}")
            raise
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle analysis-related messages"""
        if message.message_type == "analyze_request":
            # Perform analysis
            analysis = await self.think(
                f"Analyze: {message.content.get('data', '')}",
                message.content
            )
            
            return AgentMessage(
                sender=self.id,
                recipient=message.sender,
                message_type="analysis_response",
                content={"analysis": analysis},
                requires_response=False
            )
        
        return None


class ExecutorAgent(BaseAgent):
    """Agent specialized in executing actions"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Action Executor",
            role=AgentRole.EXECUTOR,
            capabilities=[
                AgentCapability.SUPPLIER_MANAGEMENT,
                AgentCapability.QUOTE_PROCESSING,
                AgentCapability.SYSTEM_INTEGRATION
            ]
        )
    
    async def process_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute actions based on task requirements"""
        start_time = datetime.utcnow()
        
        try:
            if task.task_type == TaskType.ACTION:
                # Determine action type
                action_plan = await self.think(
                    f"Create action plan for: {task.description}",
                    context
                )
                
                # Simulate action execution
                await asyncio.sleep(2)  # Simulate work
                
                result = {
                    "action_taken": True,
                    "action_plan": action_plan,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            elif task.task_type == TaskType.INTEGRATION:
                # Handle integration tasks
                integration_steps = await self.think(
                    f"Plan integration steps for: {task.description}",
                    context
                )
                
                result = {
                    "integration_planned": True,
                    "steps": integration_steps
                }
            
            else:
                result = {"error": f"Unsupported task type for executor: {task.task_type}"}
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(True, duration)
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(False, duration)
            logger.error(f"ExecutorAgent failed: {str(e)}")
            raise
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle execution-related messages"""
        if message.message_type == "execute_request":
            # Execute action
            result = await self.process_task(
                Task(
                    name=message.content.get("action", ""),
                    task_type=TaskType.ACTION
                ),
                message.content
            )
            
            return AgentMessage(
                sender=self.id,
                recipient=message.sender,
                message_type="execution_response",
                content=result,
                requires_response=False
            )
        
        return None


class CoordinatorAgent(BaseAgent):
    """Agent that coordinates other agents"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Team Coordinator",
            role=AgentRole.COORDINATOR,
            capabilities=[
                AgentCapability.WORKFLOW_AUTOMATION,
                AgentCapability.DECISION_MAKING
            ]
        )
        self.team: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    def add_team_member(self, agent: BaseAgent) -> None:
        """Add an agent to the team"""
        self.team[agent.id] = agent
        logger.info(f"Added {agent.name} ({agent.role.value}) to team")
    
    async def process_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate task execution across team"""
        start_time = datetime.utcnow()
        
        try:
            # Determine which agents are needed
            agent_selection = await self.think(
                f"Select agents needed for task: {task.description}. Available agents: {[f'{a.name} ({a.role.value})' for a in self.team.values()]}",
                context
            )
            
            # Create workflow
            workflow_id = str(uuid.uuid4())
            self.active_workflows[workflow_id] = {
                "task": task,
                "agents": agent_selection,
                "status": "active",
                "results": {}
            }
            
            # Delegate to appropriate agents
            results = {}
            for agent_id, agent in self.team.items():
                if agent.role.value in agent_selection.lower():
                    agent_result = await agent.process_task(task, context)
                    results[agent.name] = agent_result
            
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["results"] = results
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(True, duration)
            
            return {
                "workflow_id": workflow_id,
                "agents_used": list(results.keys()),
                "results": results
            }
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.update_metrics(False, duration)
            logger.error(f"CoordinatorAgent failed: {str(e)}")
            raise
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route messages between agents"""
        if message.recipient in self.team:
            # Forward to specific agent
            response = await self.team[message.recipient].handle_message(message)
            return response
        elif message.message_type == "broadcast":
            # Send to all agents
            responses = []
            for agent in self.team.values():
                response = await agent.handle_message(message)
                if response:
                    responses.append(response)
            
            return AgentMessage(
                sender=self.id,
                recipient=message.sender,
                message_type="broadcast_responses",
                content={"responses": [r.__dict__ for r in responses]},
                requires_response=False
            )
        
        return None


class AgentOrchestrator:
    """Main orchestrator for the agent system"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.coordinator: Optional[CoordinatorAgent] = None
        self.planning_service = PlanningService()
        self.active_plans: Dict[str, Plan] = {}
        
    def initialize_default_team(self) -> None:
        """Initialize default team of agents"""
        # Create coordinator
        self.coordinator = CoordinatorAgent("coordinator-001")
        self.agents[self.coordinator.id] = self.coordinator
        
        # Create specialized agents
        planner = PlannerAgent("planner-001")
        analyzer = AnalyzerAgent("analyzer-001")
        executor = ExecutorAgent("executor-001")
        
        # Add to orchestrator
        self.agents[planner.id] = planner
        self.agents[analyzer.id] = analyzer
        self.agents[executor.id] = executor
        
        # Add to coordinator's team
        self.coordinator.add_team_member(planner)
        self.coordinator.add_team_member(analyzer)
        self.coordinator.add_team_member(executor)
        
        logger.info("Initialized default agent team")
    
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a high-level request"""
        if context is None:
            context = {}
        
        # Create initial plan
        plan = await self.planning_service.create_plan(
            goal=request,
            context=context
        )
        
        self.active_plans[plan.id] = plan
        
        # Execute plan using coordinator
        if self.coordinator:
            results = []
            for task in plan.tasks:
                if task.can_start([t.id for t in plan.tasks if t.status == PlanStatus.COMPLETED]):
                    task_result = await self.coordinator.process_task(task, context)
                    results.append({
                        "task": task.name,
                        "result": task_result
                    })
                    task.status = PlanStatus.COMPLETED
            
            return {
                "plan_id": plan.id,
                "request": request,
                "results": results,
                "status": "completed"
            }
        else:
            return {
                "error": "No coordinator available",
                "plan_id": plan.id
            }
    
    async def autonomous_loop(self, max_iterations: int = 10) -> None:
        """Run autonomous processing loop"""
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Check for pending tasks in active plans
            for plan_id, plan in self.active_plans.items():
                if plan.status == PlanStatus.IN_PROGRESS:
                    # Get ready tasks
                    completed_ids = [t.id for t in plan.tasks if t.status == PlanStatus.COMPLETED]
                    ready_tasks = plan.get_ready_tasks(completed_ids)
                    
                    if ready_tasks and self.coordinator:
                        # Process ready tasks
                        for task in ready_tasks[:3]:  # Process up to 3 tasks at once
                            try:
                                result = await self.coordinator.process_task(task, plan.context)
                                task.status = PlanStatus.COMPLETED
                                task.outputs = result
                                logger.info(f"Completed task: {task.name}")
                            except Exception as e:
                                task.status = PlanStatus.FAILED
                                task.error = str(e)
                                logger.error(f"Task failed: {task.name} - {str(e)}")
            
            # Sleep before next iteration
            await asyncio.sleep(5)
        
        logger.info(f"Autonomous loop completed after {iteration} iterations")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            "total_agents": len(self.agents),
            "agent_details": {}
        }
        
        for agent_id, agent in self.agents.items():
            status["agent_details"][agent_id] = {
                "name": agent.name,
                "role": agent.role.value,
                "status": agent.status,
                "capabilities": [cap.value for cap in agent.capabilities],
                "metrics": agent.performance_metrics
            }
        
        return status
    
    def get_active_plans_summary(self) -> List[Dict[str, Any]]:
        """Get summary of active plans"""
        summaries = []
        
        for plan_id, plan in self.active_plans.items():
            completed = sum(1 for t in plan.tasks if t.status == PlanStatus.COMPLETED)
            total = len(plan.tasks)
            
            summaries.append({
                "plan_id": plan_id,
                "name": plan.name,
                "progress": f"{completed}/{total} tasks",
                "status": plan.status.value
            })
        
        return summaries


# Singleton instance
agent_orchestrator = AgentOrchestrator()