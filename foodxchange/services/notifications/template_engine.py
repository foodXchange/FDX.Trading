"""
Template Engine Module
Handles notification template rendering and management
"""

import logging
import re
from typing import Dict, List, Optional, Any
from string import Template

from .models import (
    NotificationTemplate,
    NotificationType,
    NotificationCategory,
    NotificationPriority,
    NotificationAction
)

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Manages notification templates and rendering
    """
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default notification templates"""
        default_templates = [
            NotificationTemplate(
                id="ai_analysis_complete",
                name="AI Analysis Complete",
                category=NotificationCategory.AI_ANALYSIS,
                type=NotificationType.SUCCESS,
                priority=NotificationPriority.NORMAL,
                title_template="AI Analysis Complete: ${analysis_type}",
                message_template="Your ${analysis_type} analysis for ${item_name} has been completed. ${summary}",
                action_templates=[
                    {"label": "View Results", "url": "/analysis/${analysis_id}", "style": "primary"},
                    {"label": "Download Report", "url": "/analysis/${analysis_id}/download", "style": "secondary"}
                ]
            ),
            NotificationTemplate(
                id="new_supplier_match",
                name="New Supplier Match",
                category=NotificationCategory.SUPPLIERS,
                type=NotificationType.INFO,
                priority=NotificationPriority.NORMAL,
                title_template="New Supplier Match: ${supplier_name}",
                message_template="${supplier_name} matches your requirements for ${product_category}. They offer ${certifications}.",
                action_templates=[
                    {"label": "View Profile", "url": "/suppliers/${supplier_id}", "style": "primary"},
                    {"label": "Contact", "url": "/suppliers/${supplier_id}/contact", "style": "secondary"}
                ]
            ),
            NotificationTemplate(
                id="project_update",
                name="Project Update",
                category=NotificationCategory.PROJECTS,
                type=NotificationType.INFO,
                priority=NotificationPriority.NORMAL,
                title_template="Project Update: ${project_name}",
                message_template="${update_message}",
                action_templates=[
                    {"label": "View Project", "url": "/projects/${project_id}", "style": "primary"}
                ]
            ),
            NotificationTemplate(
                id="security_alert",
                name="Security Alert",
                category=NotificationCategory.SECURITY,
                type=NotificationType.WARNING,
                priority=NotificationPriority.HIGH,
                title_template="Security Alert: ${alert_type}",
                message_template="${alert_message}",
                action_templates=[
                    {"label": "Review", "url": "/security/alerts/${alert_id}", "style": "danger"}
                ]
            ),
            NotificationTemplate(
                id="system_maintenance",
                name="System Maintenance",
                category=NotificationCategory.SYSTEM,
                type=NotificationType.WARNING,
                priority=NotificationPriority.NORMAL,
                title_template="Scheduled Maintenance",
                message_template="System maintenance scheduled for ${maintenance_date} from ${start_time} to ${end_time}.",
                action_templates=[
                    {"label": "Learn More", "url": "/system/maintenance", "style": "secondary"}
                ]
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
    
    def render_notification(
        self,
        template_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a notification from template"""
        try:
            template = self.templates.get(template_id)
            if not template:
                logger.error(f"Template {template_id} not found")
                return None
            
            # Render title and message
            title = self._render_string(template.title_template, context)
            message = self._render_string(template.message_template, context)
            
            # Render actions
            actions = []
            for action_template in template.action_templates:
                action = NotificationAction(
                    label=self._render_string(action_template.get("label", ""), context),
                    url=self._render_string(action_template.get("url", ""), context),
                    action_type=action_template.get("action_type", "link"),
                    style=action_template.get("style", "primary")
                )
                actions.append(action)
            
            # Combine metadata
            metadata = {**template.default_metadata, **context.get("metadata", {})}
            
            return {
                "title": title,
                "message": message,
                "type": template.type,
                "category": template.category,
                "priority": template.priority,
                "actions": actions,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error rendering notification: {e}")
            return None
    
    def _render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with context"""
        try:
            # Use safe substitution to avoid KeyError
            template = Template(template_str)
            return template.safe_substitute(**context)
        except Exception as e:
            logger.error(f"Error rendering string: {e}")
            return template_str
    
    def add_template(self, template: NotificationTemplate):
        """Add a new template"""
        self.templates[template.id] = template
        logger.info(f"Added template {template.id}")
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get a specific template"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[NotificationCategory] = None) -> List[NotificationTemplate]:
        """List available templates"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    def create_custom_notification(
        self,
        title: str,
        message: str,
        context: Dict[str, Any],
        type: NotificationType = NotificationType.INFO,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        actions: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Create a custom notification without a template"""
        try:
            # Render title and message
            rendered_title = self._render_string(title, context)
            rendered_message = self._render_string(message, context)
            
            # Create actions
            rendered_actions = []
            if actions:
                for action_data in actions:
                    action = NotificationAction(
                        label=self._render_string(action_data.get("label", ""), context),
                        url=self._render_string(action_data.get("url", ""), context),
                        action_type=action_data.get("action_type", "link"),
                        style=action_data.get("style", "primary")
                    )
                    rendered_actions.append(action)
            
            return {
                "title": rendered_title,
                "message": rendered_message,
                "type": type,
                "category": category,
                "priority": priority,
                "actions": rendered_actions,
                "metadata": context.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error creating custom notification: {e}")
            return None
    
    def validate_template(self, template: NotificationTemplate) -> List[str]:
        """Validate a notification template"""
        errors = []
        
        # Check required fields
        if not template.id:
            errors.append("Template ID is required")
        if not template.title_template:
            errors.append("Title template is required")
        if not template.message_template:
            errors.append("Message template is required")
        
        # Check for valid placeholders
        title_vars = self._extract_variables(template.title_template)
        message_vars = self._extract_variables(template.message_template)
        
        # Check action templates
        for i, action in enumerate(template.action_templates):
            if not action.get("label"):
                errors.append(f"Action {i} missing label")
            if not action.get("url"):
                errors.append(f"Action {i} missing URL")
            
            # Extract variables from actions
            if "label" in action:
                label_vars = self._extract_variables(action["label"])
            if "url" in action:
                url_vars = self._extract_variables(action["url"])
        
        return errors
    
    def _extract_variables(self, template_str: str) -> List[str]:
        """Extract variable names from template string"""
        # Match ${variable_name} pattern
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, template_str)
        return matches