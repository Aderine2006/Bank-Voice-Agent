import logging
import sys
from datetime import datetime
from typing import Any


class BankVoiceLogger:
    """Custom logger for BankVoice AI"""
    
    def __init__(self, name: str = "bankvoice"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_request(self, request_id: str, endpoint: str, method: str):
        """Log incoming request"""
        self.logger.info(f"[{request_id}] {method} {endpoint}")
    
    def log_response(self, request_id: str, status_code: int, duration_ms: float):
        """Log response"""
        self.logger.info(f"[{request_id}] Response: {status_code} ({duration_ms:.2f}ms)")
    
    def log_error(self, request_id: str, error: str, context: Any = None):
        """Log error"""
        self.logger.error(f"[{request_id}] Error: {error}")
        if context:
            self.logger.error(f"[{request_id}] Context: {context}")
    
    def log_provider_call(self, provider: str, operation: str, duration_ms: float):
        """Log provider call"""
        self.logger.info(f"[Provider] {provider} - {operation} ({duration_ms:.2f}ms)")
    
    def log_conversation(self, conversation_id: str, stage: str, intent: str):
        """Log conversation state"""
        self.logger.info(f"[{conversation_id}] Stage: {stage}, Intent: {intent}")


logger = BankVoiceLogger()
