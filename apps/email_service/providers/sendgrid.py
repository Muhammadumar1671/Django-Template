"""SendGrid email provider implementation."""

from typing import Dict, Any, Optional
import requests
from .base import BaseEmailProvider


class SendGridProvider(BaseEmailProvider):
    """SendGrid email provider."""
    
    API_URL = "https://api.sendgrid.com/v3/mail/send"
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send email via SendGrid."""
        
        from_email = from_email or self.config.get('default_from_email')
        from_name = from_name or self.config.get('default_from_name', '')
        
        payload = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {
                "email": from_email,
                "name": from_name
            },
            "content": [{
                "type": "text/html",
                "value": html_content
            }]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            
            if response.status_code == 202:
                message_id = response.headers.get('X-Message-Id', '')
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': 'sendgrid'
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'provider': 'sendgrid'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'sendgrid'
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
        """Send template email via SendGrid."""
        
        from_email = from_email or self.config.get('default_from_email')
        from_name = from_name or self.config.get('default_from_name', '')
        
        payload = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "dynamic_template_data": template_data
            }],
            "from": {
                "email": from_email,
                "name": from_name
            },
            "template_id": template_id
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            
            if response.status_code == 202:
                message_id = response.headers.get('X-Message-Id', '')
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': 'sendgrid'
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'provider': 'sendgrid'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'sendgrid'
            }
