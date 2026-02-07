"""
Celery tasks for email service.

These tasks handle async email sending and maintenance operations.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    autoretry_for=(Exception,),
)
def send_email_task(
    self,
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = None,
    from_name: str = None,
    log_email: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Async task to send an email.

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
    from apps.email_service.services import EmailService

    try:
        result = EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            from_email=from_email,
            from_name=from_name,
            log_email=log_email,
            **kwargs
        )

        if not result['success']:
            logger.warning(f"Email to {to_email} failed: {result.get('error')}")
            # Retry if failed
            raise Exception(result.get('error', 'Unknown error'))

        logger.info(f"Email sent successfully to {to_email}")
        return result

    except Exception as exc:
        logger.error(f"Error sending email to {to_email}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def send_template_email_task(
    self,
    to_email: str,
    template_name: str,
    context: Dict[str, Any],
    subject: str = None,
    from_email: str = None,
    from_name: str = None,
    log_email: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Async task to send a template-based email.

    Args:
        to_email: Recipient email
        template_name: Template identifier
        context: Template context data
        subject: Email subject (optional)
        from_email: Sender email (optional)
        from_name: Sender name (optional)
        log_email: Whether to log this email

    Returns:
        dict: Result from provider
    """
    from apps.email_service.services import EmailService

    try:
        result = EmailService.send_template_email(
            to_email=to_email,
            template_name=template_name,
            context=context,
            subject=subject,
            from_email=from_email,
            from_name=from_name,
            log_email=log_email,
            **kwargs
        )

        if not result['success']:
            logger.warning(f"Template email '{template_name}' to {to_email} failed: {result.get('error')}")
            raise Exception(result.get('error', 'Unknown error'))

        logger.info(f"Template email '{template_name}' sent successfully to {to_email}")
        return result

    except Exception as exc:
        logger.error(f"Error sending template email to {to_email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@shared_task(bind=True)
def send_verification_email_task(self, user_id: int, token: str):
    """
    Async task to send email verification email.

    Args:
        user_id: User ID
        token: Verification token
    """
    from django.contrib.auth import get_user_model
    from django.conf import settings

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {'success': False, 'error': 'User not found'}

    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': getattr(settings, 'SITE_NAME', 'Your App'),
    }

    return send_template_email_task.apply_async(
        kwargs={
            'to_email': user.email,
            'template_name': 'emails/verify_email.html',
            'context': context,
            'subject': 'Verify your email address',
        }
    )


@shared_task(bind=True)
def send_password_reset_email_task(self, user_id: int, token: str):
    """
    Async task to send password reset email.

    Args:
        user_id: User ID
        token: Reset token
    """
    from django.contrib.auth import get_user_model
    from django.conf import settings

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {'success': False, 'error': 'User not found'}

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': getattr(settings, 'SITE_NAME', 'Your App'),
    }

    return send_template_email_task.apply_async(
        kwargs={
            'to_email': user.email,
            'template_name': 'emails/password_reset.html',
            'context': context,
            'subject': 'Reset your password',
        }
    )


@shared_task(bind=True)
def send_welcome_email_task(self, user_id: int):
    """
    Async task to send welcome email.

    Args:
        user_id: User ID
    """
    from django.contrib.auth import get_user_model
    from django.conf import settings

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {'success': False, 'error': 'User not found'}

    context = {
        'user': user,
        'site_name': getattr(settings, 'SITE_NAME', 'Your App'),
        'login_url': f"{settings.FRONTEND_URL}/login",
    }

    return send_template_email_task.apply_async(
        kwargs={
            'to_email': user.email,
            'template_name': 'emails/welcome.html',
            'context': context,
            'subject': 'Welcome to our platform!',
        }
    )


@shared_task
def cleanup_old_email_logs():
    """
    Cleanup old email logs (older than 90 days).

    This is a periodic task that runs daily via Celery Beat.
    """
    from apps.email_service.models import EmailLog

    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count, _ = EmailLog.objects.filter(created_at__lt=cutoff_date).delete()

    logger.info(f"Cleaned up {deleted_count} old email logs")
    return {'deleted_count': deleted_count}
