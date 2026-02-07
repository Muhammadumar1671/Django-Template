"""Base email provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseEmailProvider(ABC):
    """Base class for email providers."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize provider with API key and optional config."""
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Returns:
            dict: {
                'success': bool,
                'message_id': str (if successful),
                'error': str (if failed)
            }
        """
        pass
    
    @abstractmethod
    def send_template_email(
        self,
        to_email: str,
        template_id: str,
        template_data: Dict[str, Any],
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an email using a template.
        
        Returns:
            dict: {
                'success': bool,
                'message_id': str (if successful),
                'error': str (if failed)
            }
        """
        pass
