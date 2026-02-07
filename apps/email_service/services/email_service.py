"""Main email service."""

from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone
from django.template import Template, Context
from django.template.loader import render_to_string
from apps.email_service.models import EmailLog, EmailTemplate
from apps.email_service.providers import SendGridProvider, ResendProvider, SMTPProvider


class EmailService:
    """
    Generic email service that works with multiple providers.
    
    Configure in settings.py:
    
    EMAIL_PROVIDER = 'sendgrid'  # or 'resend', 'smtp'
    EMAIL_PROVIDER_API_KEY = 'your-api-key'
    DEFAULT_FROM_EMAIL = 'noreply@example.com'
    DEFAULT_FROM_NAME = 'Your App'
    """
    
    @classmethod
    def _get_provider(cls):
        """Get configured email provider."""
        provider_name = getattr(settings, 'EMAIL_PROVIDER', 'smtp').lower()
        api_key = getattr(settings, 'EMAIL_PROVIDER_API_KEY', '')
        
        config = {
            'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            'default_from_name': getattr(settings, 'DEFAULT_FROM_NAME', ''),
        }
        
        if provider_name == 'sendgrid':
            return SendGridProvider(api_key, **config)
        elif provider_name == 'resend':
            return ResendProvider(api_key, **config)
        elif provider_name == 'smtp':
            return SMTPProvider(**config)
        else:
            raise ValueError(f"Unknown email provider: {provider_name}")
    
    @classmethod
    def send_email(
        cls,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        log_email: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            from_email: Sender email (optional)
            from_name: Sender name (optional)
            log_email: Whether to log this email
            
        Returns:
            dict: Result from provider
        """
        provider = cls._get_provider()
        
        # Create email log
        email_log = None
        if log_email:
            email_log = EmailLog.objects.create(
                to_email=to_email,
                from_email=from_email or provider.config.get('default_from_email'),
                subject=subject,
                provider=provider.__class__.__name__.replace('Provider', '').lower(),
                status='pending'
            )
        
        # Send email
        result = provider.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            from_email=from_email,
            from_name=from_name,
            **kwargs
        )
        
        # Update log
        if log_email and email_log:
            if result['success']:
                email_log.status = 'sent'
                email_log.provider_message_id = result.get('message_id', '')
                email_log.sent_at = timezone.now()
            else:
                email_log.status = 'failed'
                email_log.error_message = result.get('error', '')
            email_log.save()
        
        return result
    
    @classmethod
    def _get_template_from_db(cls, template_name: str) -> Optional[EmailTemplate]:
        """
        Get email template from database.

        Args:
            template_name: Template identifier (e.g., 'welcome', 'password_reset')

        Returns:
            EmailTemplate object or None
        """
        try:
            return EmailTemplate.objects.filter(name=template_name, is_active=True).first()
        except Exception:
            return None

    @classmethod
    def _render_template_string(cls, template_string: str, context: Dict[str, Any]) -> str:
        """Render a template string with context."""
        template = Template(template_string)
        return template.render(Context(context))

    @classmethod
    def send_template_email(
        cls,
        to_email: str,
        template_name: str,
        context: Dict[str, Any],
        subject: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        log_email: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send email using template (database or static file).

        Template source is controlled by USE_DB_EMAIL_TEMPLATES setting:
        - 'db' (default): Try database first, fallback to static files
        - 'static': Only use static template files
        - 'db_only': Only use database templates (raises error if not found)

        Args:
            to_email: Recipient email
            template_name: Template identifier (e.g., 'welcome') or path (e.g., 'emails/welcome.html')
            context: Template context data
            subject: Email subject (required if using static template, optional for DB template)
            from_email: Sender email (optional)
            from_name: Sender name (optional)
            log_email: Whether to log this email

        Returns:
            dict: Result from provider
        """
        template_source = getattr(settings, 'USE_DB_EMAIL_TEMPLATES', 'db')
        db_template = None
        html_content = None
        email_subject = None

        # Determine template source based on configuration
        if template_source in ['db', 'db_only']:
            db_template = cls._get_template_from_db(template_name)

        if db_template:
            # Use database template
            html_content = cls._render_template_string(db_template.html_content, context)
            email_subject = cls._render_template_string(db_template.subject, context)
        elif template_source == 'db_only':
            # DB-only mode but template not found
            raise ValueError(f"Database template '{template_name}' not found and USE_DB_EMAIL_TEMPLATES is set to 'db_only'")
        else:
            # Use static template file (either 'static' mode or 'db' mode with no DB template)
            if not subject:
                raise ValueError("Subject is required when using static templates")

            html_content = render_to_string(template_name, context)
            email_subject = subject

        # Send email
        return cls.send_email(
            to_email=to_email,
            subject=email_subject,
            html_content=html_content,
            from_email=from_email,
            from_name=from_name,
            log_email=log_email,
            **kwargs
        )
    
    # Convenience methods for authentication emails
    
    @classmethod
    def send_verification_email(cls, user, token: str):
        """Send email verification email."""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Your App'),
        }
        
        return cls.send_template_email(
            to_email=user.email,
            template_name='emails/verify_email.html',
            context=context,
            subject='Verify your email address',
        )
    
    @classmethod
    def send_password_reset_email(cls, user, token: str):
        """Send password reset email."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Your App'),
        }
        
        return cls.send_template_email(
            to_email=user.email,
            template_name='emails/password_reset.html',
            context=context,
            subject='Reset your password',
        )
    
    @classmethod
    def send_welcome_email(cls, user):
        """Send welcome email."""
        context = {
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'Your App'),
            'login_url': f"{settings.FRONTEND_URL}/login",
        }
        
        return cls.send_template_email(
            to_email=user.email,
            template_name='emails/welcome.html',
            context=context,
            subject='Welcome to our platform!',
        )
