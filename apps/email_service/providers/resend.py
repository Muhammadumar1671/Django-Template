"""Resend email provider implementation."""

from typing import Dict, Any, Optional
import requests
from .base import BaseEmailProvider


class ResendProvider(BaseEmailProvider):
    """Resend email provider."""
    
    API_URL = "https://api.resend.com/emails"
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send email via Resend."""
        
        from_email = from_email or self.config.get('default_from_email')
        from_name = from_name or self.config.get('default_from_name', '')
        
        # Format from address
        if from_name:
            from_address = f"{from_name} <{from_email}>"
        else:
            from_address = from_email
        
        payload = {
            "from": from_address,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message_id': data.get('id', ''),
                    'provider': 'resend'
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'provider': 'resend'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'resend'
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
        Send template email via Resend.
        Note: Resend uses React Email templates, not template IDs.
        This is a placeholder - implement based on your template system.
        """
        # For Resend, you'd typically render the template yourself
        # and pass the HTML to send_email
        raise NotImplementedError(
            "Resend uses React Email templates. "
            "Render your template to HTML and use send_email() instead."
        )
