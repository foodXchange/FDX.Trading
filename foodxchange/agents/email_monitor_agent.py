"""
Email Monitoring Agent - Agentic Loop POC
Autonomous agent that monitors supplier emails and updates the database
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from dataclasses import dataclass, asdict

from sqlalchemy.orm import Session
from foodxchange.database import get_db
from foodxchange.models.supplier import Supplier
from foodxchange.models.email import Email
from foodxchange.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class AgentState(Enum):
    IDLE = "idle"
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    DECIDING = "deciding"
    ACTING = "acting"
    EVALUATING = "evaluating"
    ERROR = "error"
    TERMINATED = "terminated"


class EmailIntent(Enum):
    QUOTE_RESPONSE = "quote_response"
    PRICE_UPDATE = "price_update"
    PRODUCT_UPDATE = "product_update"
    CERTIFICATION_UPDATE = "certification_update"
    CONTACT_UPDATE = "contact_update"
    GENERAL_INQUIRY = "general_inquiry"
    UNKNOWN = "unknown"


@dataclass
class AgentMetrics:
    total_emails_processed: int = 0
    successful_updates: int = 0
    failed_updates: int = 0
    total_runtime_seconds: float = 0
    last_run_timestamp: Optional[datetime] = None
    error_count: int = 0
    
    def to_dict(self):
        data = asdict(self)
        if self.last_run_timestamp:
            data['last_run_timestamp'] = self.last_run_timestamp.isoformat()
        return data


@dataclass
class EmailProcessingResult:
    email_id: str
    supplier_id: Optional[int]
    intent: EmailIntent
    confidence: float
    extracted_data: Dict[str, Any]
    actions_taken: List[str]
    success: bool
    error_message: Optional[str] = None


class SupplierEmailMonitorAgent:
    """
    Agentic loop implementation for monitoring and processing supplier emails
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.state = AgentState.IDLE
        self.metrics = AgentMetrics()
        self.is_running = False
        self.loop_interval = 300  # 5 minutes default
        self.max_emails_per_cycle = 50
        self.confidence_threshold = 0.7
        self._state_history: List[Dict[str, Any]] = []
        
    async def start(self):
        """Start the agent loop"""
        logger.info("Starting Supplier Email Monitor Agent")
        self.is_running = True
        self.metrics.last_run_timestamp = datetime.utcnow()
        
        while self.is_running:
            try:
                await self._run_cycle()
                await asyncio.sleep(self.loop_interval)
            except Exception as e:
                logger.error(f"Agent cycle error: {str(e)}")
                self.state = AgentState.ERROR
                self.metrics.error_count += 1
                await self._handle_error(e)
                
    async def stop(self):
        """Gracefully stop the agent"""
        logger.info("Stopping Supplier Email Monitor Agent")
        self.is_running = False
        self.state = AgentState.TERMINATED
        
    async def _run_cycle(self):
        """Execute one complete agent loop cycle"""
        cycle_start = datetime.utcnow()
        self._log_state_transition(AgentState.OBSERVING)
        
        try:
            # OBSERVE: Fetch unprocessed emails
            emails = await self._observe_emails()
            
            if not emails:
                logger.info("No new emails to process")
                return
                
            # ANALYZE: Process emails with AI
            self._log_state_transition(AgentState.ANALYZING)
            analysis_results = await self._analyze_emails(emails)
            
            # DECIDE: Determine actions based on analysis
            self._log_state_transition(AgentState.DECIDING)
            decisions = await self._make_decisions(analysis_results)
            
            # ACT: Execute database updates and actions
            self._log_state_transition(AgentState.ACTING)
            action_results = await self._execute_actions(decisions)
            
            # EVALUATE: Assess results and update metrics
            self._log_state_transition(AgentState.EVALUATING)
            await self._evaluate_results(action_results)
            
        finally:
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self.metrics.total_runtime_seconds += cycle_duration
            self._log_state_transition(AgentState.IDLE)
            
    async def _observe_emails(self) -> List[Email]:
        """Fetch unprocessed supplier emails"""
        # In production, this would connect to IMAP/Exchange
        # For POC, we'll query the database for unprocessed emails
        
        unprocessed_emails = self.db.query(Email).filter(
            Email.processed == False,
            Email.email_type == 'supplier'
        ).limit(self.max_emails_per_cycle).all()
        
        logger.info(f"Found {len(unprocessed_emails)} unprocessed emails")
        return unprocessed_emails
        
    async def _analyze_emails(self, emails: List[Email]) -> List[EmailProcessingResult]:
        """Analyze emails using Azure OpenAI"""
        results = []
        
        for email in emails:
            try:
                # Simulate AI analysis - in production, call Azure OpenAI
                result = await self._analyze_single_email(email)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze email {email.id}: {str(e)}")
                results.append(EmailProcessingResult(
                    email_id=str(email.id),
                    supplier_id=None,
                    intent=EmailIntent.UNKNOWN,
                    confidence=0.0,
                    extracted_data={},
                    actions_taken=[],
                    success=False,
                    error_message=str(e)
                ))
                
        return results
        
    async def _analyze_single_email(self, email: Email) -> EmailProcessingResult:
        """Analyze a single email (POC simulation)"""
        # In production, this would call Azure OpenAI
        # For POC, we'll simulate the analysis
        
        # Simulate intent detection
        if "quote" in email.subject.lower():
            intent = EmailIntent.QUOTE_RESPONSE
        elif "price" in email.subject.lower():
            intent = EmailIntent.PRICE_UPDATE
        elif "product" in email.subject.lower():
            intent = EmailIntent.PRODUCT_UPDATE
        else:
            intent = EmailIntent.GENERAL_INQUIRY
            
        # Simulate supplier matching
        supplier = self.db.query(Supplier).filter(
            Supplier.email == email.sender_email
        ).first()
        
        return EmailProcessingResult(
            email_id=str(email.id),
            supplier_id=supplier.id if supplier else None,
            intent=intent,
            confidence=0.85,  # Simulated confidence
            extracted_data={
                "subject": email.subject,
                "sender": email.sender_email,
                "content_preview": email.body[:200] if email.body else ""
            },
            actions_taken=[],
            success=True
        )
        
    async def _make_decisions(self, analysis_results: List[EmailProcessingResult]) -> List[Dict[str, Any]]:
        """Decide what actions to take based on analysis"""
        decisions = []
        
        for result in analysis_results:
            if result.confidence < self.confidence_threshold:
                decisions.append({
                    "result": result,
                    "action": "flag_for_review",
                    "reason": f"Low confidence: {result.confidence}"
                })
                continue
                
            if not result.supplier_id:
                decisions.append({
                    "result": result,
                    "action": "create_new_supplier",
                    "reason": "Unknown supplier"
                })
                continue
                
            # Decide based on intent
            if result.intent == EmailIntent.QUOTE_RESPONSE:
                decisions.append({
                    "result": result,
                    "action": "create_quote",
                    "reason": "Quote response detected"
                })
            elif result.intent == EmailIntent.PRICE_UPDATE:
                decisions.append({
                    "result": result,
                    "action": "update_pricing",
                    "reason": "Price update detected"
                })
            else:
                decisions.append({
                    "result": result,
                    "action": "update_supplier_notes",
                    "reason": f"General update: {result.intent.value}"
                })
                
        return decisions
        
    async def _execute_actions(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute the decided actions"""
        results = []
        
        for decision in decisions:
            try:
                if decision["action"] == "update_supplier_notes":
                    await self._update_supplier_notes(
                        decision["result"].supplier_id,
                        decision["result"].extracted_data
                    )
                    decision["result"].actions_taken.append("updated_supplier_notes")
                    
                # Mark email as processed
                email = self.db.query(Email).get(decision["result"].email_id)
                if email:
                    email.processed = True
                    email.processed_at = datetime.utcnow()
                    self.db.commit()
                    
                self.metrics.successful_updates += 1
                results.append({"decision": decision, "success": True})
                
            except Exception as e:
                logger.error(f"Action execution failed: {str(e)}")
                self.metrics.failed_updates += 1
                results.append({"decision": decision, "success": False, "error": str(e)})
                
        return results
        
    async def _update_supplier_notes(self, supplier_id: int, data: Dict[str, Any]):
        """Update supplier notes with extracted data"""
        supplier = self.db.query(Supplier).get(supplier_id)
        if supplier:
            current_notes = supplier.notes or ""
            new_note = f"\n[{datetime.utcnow().isoformat()}] Email Update: {data.get('subject', 'No subject')}"
            supplier.notes = current_notes + new_note
            self.db.commit()
            
    async def _evaluate_results(self, action_results: List[Dict[str, Any]]):
        """Evaluate the results of the cycle"""
        successful = sum(1 for r in action_results if r.get("success", False))
        failed = len(action_results) - successful
        
        self.metrics.total_emails_processed += len(action_results)
        
        logger.info(f"Cycle complete: {successful} successful, {failed} failed")
        
        # Store evaluation for learning (in production, this could feed back to AI)
        evaluation = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_processed": len(action_results),
            "successful": successful,
            "failed": failed,
            "state_history": self._state_history[-10:]  # Last 10 states
        }
        
        # In production, store this for analysis and improvement
        
    async def _handle_error(self, error: Exception):
        """Handle errors and potentially recover"""
        logger.error(f"Agent error: {str(error)}")
        
        # Simple exponential backoff
        wait_time = min(300, 10 * (2 ** min(self.metrics.error_count, 5)))
        logger.info(f"Waiting {wait_time} seconds before retry")
        await asyncio.sleep(wait_time)
        
        # Reset to idle state to attempt recovery
        self.state = AgentState.IDLE
        
    def _log_state_transition(self, new_state: AgentState):
        """Log state transitions for observability"""
        old_state = self.state
        self.state = new_state
        
        transition = {
            "timestamp": datetime.utcnow().isoformat(),
            "from_state": old_state.value,
            "to_state": new_state.value
        }
        
        self._state_history.append(transition)
        logger.debug(f"State transition: {old_state.value} -> {new_state.value}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "metrics": self.metrics.to_dict(),
            "config": {
                "loop_interval": self.loop_interval,
                "max_emails_per_cycle": self.max_emails_per_cycle,
                "confidence_threshold": self.confidence_threshold
            }
        }


# Agent Manager for controlling multiple agents
class AgentManager:
    """Manages multiple agent instances"""
    
    def __init__(self):
        self.agents: Dict[str, SupplierEmailMonitorAgent] = {}
        
    async def create_agent(self, agent_id: str, db_session: Session) -> SupplierEmailMonitorAgent:
        """Create a new agent instance"""
        if agent_id in self.agents:
            raise ValueError(f"Agent {agent_id} already exists")
            
        agent = SupplierEmailMonitorAgent(db_session)
        self.agents[agent_id] = agent
        return agent
        
    async def start_agent(self, agent_id: str):
        """Start a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        agent = self.agents[agent_id]
        asyncio.create_task(agent.start())
        
    async def stop_agent(self, agent_id: str):
        """Stop a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        await self.agents[agent_id].stop()
        
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }


# Global agent manager instance
agent_manager = AgentManager()