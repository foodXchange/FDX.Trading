"""
Error Handling Service Package
Provides intelligent error handling for the FoodXchange platform
"""

from .error_handler import IntelligentErrorHandler
from .models import (
    ErrorType,
    ErrorSeverity,
    RecoveryAction,
    ErrorContext,
    ErrorDetails,
    RecoveryOption,
    ErrorNotification
)
from .error_analyzer import ErrorAnalyzer
from .recovery_manager import RecoveryManager
from .error_logger import ErrorLogger

__all__ = [
    'IntelligentErrorHandler',
    'ErrorType',
    'ErrorSeverity',
    'RecoveryAction',
    'ErrorContext',
    'ErrorDetails',
    'RecoveryOption',
    'ErrorNotification',
    'ErrorAnalyzer',
    'RecoveryManager',
    'ErrorLogger'
]