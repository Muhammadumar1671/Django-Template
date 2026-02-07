"""SMTP email provider implementation."""

from typing import Dict, Any, Optional
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .base import BaseEmailProvider


class SMTPProvider(BaseEmailProvider):
    """SMTP email provider using Django's email backend."""
    
    def __init__(self, **kwargs):
        """Initialize SMTP provider (uses Django settings)."""
        self.config = kwargs
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send email via SMTP."""
        
        from_email = from_email or self.config.get('default_from_email') or settings.DEFAULT_FROM_EMAIL
        
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=html_content,  # Plain text fallback
                from_email=from_email,
                to=[to_email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return {
                'success': True,
                'message_id': '',  # SMTP doesn't return message ID
                'provider': 'smtp'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'smtp'
            }
    
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
        Send template email via SMTP.
        Requires template rendering before calling.
        """
        raise NotImplementedError(
            "SMTP provider requires pre-rendered HTML. "
            "Render your template and use send_email() instead."
        )
