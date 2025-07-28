"""
One-Person Company Orchestrator Agent
Coordinates all other agents to automate the entire sourcing workflow
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import json

from sqlalchemy.orm import Session
from foodxchange.database import get_db
from foodxchange.models.user import User
from foodxchange.models.supplier import Supplier
from foodxchange.models.rfq import RFQ
from foodxchange.models.quote import Quote

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks the orchestrator can handle"""
    SUPPLIER_DISCOVERY = "supplier_discovery"
    EMAIL_MONITORING = "email_monitoring"
    RFQ_CREATION = "rfq_creation"
    QUOTE_COMPARISON = "quote_comparison"
    PRICE_TRACKING = "price_tracking"
    DATA_IMPORT = "data_import"
    REPORT_GENERATION = "report_generation"


class TaskStatus(Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


@dataclass
class AutomationTask:
    """Represents a task to be automated"""
    id: str
    type: TaskType
    status: TaskStatus
    config: Dict[str, Any]
    scheduled_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AutomationMetrics:
    """Metrics for the automation system"""
    tasks_created: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_time_saved_hours: float = 0.0
    emails_processed: int = 0
    rfqs_created: int = 0
    quotes_analyzed: int = 0
    suppliers_discovered: int = 0
    last_run: Optional[datetime] = None


class OnePersonOrchestrator:
    """
    Main orchestrator that coordinates all agents for one-person company automation
    """
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.is_running = False
        self.tasks: Dict[str, AutomationTask] = {}
        self.metrics = AutomationMetrics()
        self.daily_schedule = self._get_default_schedule()
        
    def _get_default_schedule(self) -> List[Dict[str, Any]]:
        """Get default daily automation schedule"""
        return [
            {
                "time": "08:00",
                "task": TaskType.EMAIL_MONITORING,
                "config": {"process_unread": True, "max_emails": 50}
            },
            {
                "time": "09:00",
                "task": TaskType.SUPPLIER_DISCOVERY,
                "config": {"max_suppliers": 5, "categories": ["auto"]}
            },
            {
                "time": "14:00",
                "task": TaskType.PRICE_TRACKING,
                "config": {"check_all_products": True}
            },
            {
                "time": "16:00",
                "task": TaskType.QUOTE_COMPARISON,
                "config": {"auto_notify": True}
            },
            {
                "time": "17:00",
                "task": TaskType.REPORT_GENERATION,
                "config": {"type": "daily_summary"}
            }
        ]
    
    async def start(self):
        """Start the orchestrator"""
        if self.is_running:
            logger.warning("Orchestrator is already running")
            return
            
        self.is_running = True
        logger.info(f"Starting One-Person Orchestrator for user {self.user.email}")
        
        # Start the main loop
        asyncio.create_task(self._main_loop())
        
        # Start the scheduler
        asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        """Stop the orchestrator"""
        logger.info("Stopping One-Person Orchestrator")
        self.is_running = False
        
    async def _main_loop(self):
        """Main execution loop"""
        while self.is_running:
            try:
                # Process pending tasks
                pending_tasks = [t for t in self.tasks.values() 
                               if t.status == TaskStatus.PENDING]
                
                for task in pending_tasks:
                    await self._execute_task(task)
                    
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in orchestrator main loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
                
    async def _scheduler_loop(self):
        """Scheduler loop for daily tasks"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for schedule in self.daily_schedule:
                    scheduled_time = datetime.strptime(
                        f"{current_time.date()} {schedule['time']}", 
                        "%Y-%m-%d %H:%M"
                    )
                    
                    # Check if it's time to create the task
                    if (current_time >= scheduled_time and 
                        current_time < scheduled_time + timedelta(minutes=5)):
                        
                        # Check if task already exists for today
                        task_id = f"{schedule['task'].value}_{current_time.date()}"
                        if task_id not in self.tasks:
                            task = await self.create_task(
                                schedule['task'],
                                schedule['config'],
                                scheduled_time
                            )
                            logger.info(f"Scheduled task created: {task_id}")
                
                # Wait 5 minutes before checking again
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(300)
                
    async def create_task(
        self, 
        task_type: TaskType, 
        config: Dict[str, Any],
        scheduled_time: Optional[datetime] = None
    ) -> AutomationTask:
        """Create a new automation task"""
        task_id = f"{task_type.value}_{datetime.now().timestamp()}"
        
        task = AutomationTask(
            id=task_id,
            type=task_type,
            status=TaskStatus.SCHEDULED if scheduled_time else TaskStatus.PENDING,
            config=config,
            scheduled_time=scheduled_time
        )
        
        self.tasks[task_id] = task
        self.metrics.tasks_created += 1
        
        logger.info(f"Created task: {task_id}")
        return task
        
    async def _execute_task(self, task: AutomationTask):
        """Execute a single task"""
        try:
            logger.info(f"Executing task: {task.id}")
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            # Route to appropriate handler
            if task.type == TaskType.EMAIL_MONITORING:
                result = await self._handle_email_monitoring(task.config)
            elif task.type == TaskType.SUPPLIER_DISCOVERY:
                result = await self._handle_supplier_discovery(task.config)
            elif task.type == TaskType.RFQ_CREATION:
                result = await self._handle_rfq_creation(task.config)
            elif task.type == TaskType.QUOTE_COMPARISON:
                result = await self._handle_quote_comparison(task.config)
            elif task.type == TaskType.PRICE_TRACKING:
                result = await self._handle_price_tracking(task.config)
            elif task.type == TaskType.REPORT_GENERATION:
                result = await self._handle_report_generation(task.config)
            else:
                raise ValueError(f"Unknown task type: {task.type}")
                
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            self.metrics.tasks_completed += 1
            self.metrics.last_run = datetime.now()
            
            # Estimate time saved (30 minutes per automated task)
            self.metrics.total_time_saved_hours += 0.5
            
            logger.info(f"Task completed: {task.id}")
            
        except Exception as e:
            logger.error(f"Task failed: {task.id} - {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING  # Retry
                logger.info(f"Retrying task: {task.id} (attempt {task.retry_count})")
            else:
                self.metrics.tasks_failed += 1
                
    async def _handle_email_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email monitoring task"""
        from foodxchange.agents.email_monitor_agent import SupplierEmailMonitorAgent
        
        agent = SupplierEmailMonitorAgent(self.db)
        
        # Process emails
        emails_processed = 0
        rfqs_created = 0
        quotes_found = 0
        
        # Simulate email processing (in real implementation, this would call the actual agent)
        logger.info("Processing emails...")
        await asyncio.sleep(2)  # Simulate processing time
        
        emails_processed = config.get("max_emails", 50)
        self.metrics.emails_processed += emails_processed
        
        return {
            "emails_processed": emails_processed,
            "rfqs_created": rfqs_created,
            "quotes_found": quotes_found
        }
        
    async def _handle_supplier_discovery(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle supplier discovery task"""
        max_suppliers = config.get("max_suppliers", 5)
        categories = config.get("categories", [])
        
        logger.info(f"Discovering suppliers in categories: {categories}")
        
        # Simulate web scraping with 7-second delays
        suppliers_found = []
        for i in range(min(max_suppliers, 3)):  # Limit for demo
            await asyncio.sleep(7)  # Required 7-second delay
            supplier_name = f"Auto Supplier {i+1}"
            suppliers_found.append(supplier_name)
            logger.info(f"Found supplier: {supplier_name}")
            
        self.metrics.suppliers_discovered += len(suppliers_found)
        
        return {
            "suppliers_found": suppliers_found,
            "categories_searched": categories
        }
        
    async def _handle_rfq_creation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RFQ creation task"""
        products = config.get("products", [])
        auto_send = config.get("auto_send", False)
        
        logger.info(f"Creating RFQs for {len(products)} products")
        
        rfqs_created = []
        for product in products:
            # Create RFQ in database
            rfq = RFQ(
                user_id=self.user.id,
                product_name=product,
                quantity=config.get("quantity", 100),
                delivery_date=datetime.now() + timedelta(days=30),
                status="draft"
            )
            self.db.add(rfq)
            rfqs_created.append(rfq.id)
            
        self.db.commit()
        self.metrics.rfqs_created += len(rfqs_created)
        
        return {
            "rfqs_created": len(rfqs_created),
            "auto_sent": auto_send
        }
        
    async def _handle_quote_comparison(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quote comparison task"""
        logger.info("Comparing quotes...")
        
        # Get open RFQs
        open_rfqs = self.db.query(RFQ).filter(
            RFQ.user_id == self.user.id,
            RFQ.status == "open"
        ).all()
        
        comparisons = []
        for rfq in open_rfqs:
            quotes = self.db.query(Quote).filter(Quote.rfq_id == rfq.id).all()
            if len(quotes) >= 2:
                # Find best quote
                best_quote = min(quotes, key=lambda q: q.unit_price)
                comparisons.append({
                    "rfq_id": rfq.id,
                    "product": rfq.product_name,
                    "best_price": best_quote.unit_price,
                    "savings": max(q.unit_price for q in quotes) - best_quote.unit_price
                })
                
        self.metrics.quotes_analyzed += sum(len(c) for c in comparisons)
        
        return {
            "comparisons": comparisons,
            "total_savings": sum(c["savings"] for c in comparisons)
        }
        
    async def _handle_price_tracking(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price tracking task"""
        logger.info("Tracking prices...")
        
        # Track price changes
        price_changes = []
        
        # Simulate price tracking
        await asyncio.sleep(1)
        
        return {
            "products_tracked": 0,
            "price_changes": price_changes
        }
        
    async def _handle_report_generation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report generation task"""
        report_type = config.get("type", "daily_summary")
        
        logger.info(f"Generating {report_type} report...")
        
        report = {
            "date": datetime.now().date().isoformat(),
            "type": report_type,
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "emails_processed": self.metrics.emails_processed,
                "rfqs_created": self.metrics.rfqs_created,
                "quotes_analyzed": self.metrics.quotes_analyzed,
                "suppliers_discovered": self.metrics.suppliers_discovered,
                "time_saved_hours": self.metrics.total_time_saved_hours
            },
            "summary": f"Automated {self.metrics.tasks_completed} tasks today, saving approximately {self.metrics.total_time_saved_hours:.1f} hours of manual work."
        }
        
        # Save report to database or send via email
        logger.info(f"Report generated: {report['summary']}")
        
        return report
        
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the orchestrator"""
        return {
            "is_running": self.is_running,
            "user": self.user.email,
            "metrics": {
                "tasks_created": self.metrics.tasks_created,
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "time_saved_hours": self.metrics.total_time_saved_hours,
                "last_run": self.metrics.last_run.isoformat() if self.metrics.last_run else None
            },
            "active_tasks": len([t for t in self.tasks.values() 
                               if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]),
            "scheduled_tasks": len([t for t in self.tasks.values() 
                                  if t.status == TaskStatus.SCHEDULED])
        }
        
    def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get task execution history"""
        sorted_tasks = sorted(
            self.tasks.values(), 
            key=lambda t: t.started_at or datetime.min, 
            reverse=True
        )[:limit]
        
        return [
            {
                "id": task.id,
                "type": task.type.value,
                "status": task.status.value,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error": task.error
            }
            for task in sorted_tasks
        ]


# Global orchestrator instances per user
orchestrators: Dict[int, OnePersonOrchestrator] = {}


async def get_or_create_orchestrator(user: User, db: Session) -> OnePersonOrchestrator:
    """Get or create an orchestrator for a user"""
    if user.id not in orchestrators:
        orchestrators[user.id] = OnePersonOrchestrator(db, user)
    return orchestrators[user.id]