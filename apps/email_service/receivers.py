"""Signal receivers for email actions."""

import logging
from typing import Any, Dict, Optional
from django.conf import settings
from django.dispatch import receiver

from apps.email_service.signals import send_email_signal, get_email_config_for_action
from apps.email_service.services import EmailService

logger = logging.getLogger(__name__)


@receiver(send_email_signal)
def handle_send_email(sender, **kwargs):
    """
    Generic receiver that handles all email sending.

    Args:
        sender: The sender of the signal (usually a model class)
        action: str - Action name (e.g., 'user_registered', 'password_reset')
        recipient: str - Recipient email address
        user: object - User object (optional, used for template context)
        context: dict - Additional context data for the email template
        template_name: str - Override template name (optional)
        subject: str - Override subject (optional)
    """
    # Check if emails are globally enabled
    if not getattr(settings, 'EMAIL_ENABLED', True):
        logger.info("Emails are globally disabled (EMAIL_ENABLED=False), skipping")
        return

    action = kwargs.get('action')
    recipient = kwargs.get('recipient')
    user = kwargs.get('user')
    context = kwargs.get('context', {})
    override_template = kwargs.get('template_name')
    override_subject = kwargs.get('subject')

    if not action:
        logger.error("Email signal received without 'action' parameter")
        return

    if not recipient:
        logger.error(f"Email signal for action '{action}' received without 'recipient' parameter")
        return

    # Get email configuration for this action
    email_config = get_email_config_for_action(action)

    if not email_config.get('enabled', False):
        logger.info(f"Email action '{action}' is disabled, skipping")
        return

    # Determine template and subject
    template_name = override_template or email_config.get('template_name')
    subject = override_subject or email_config.get('subject')

    if not template_name:
        logger.error(f"No template_name found for action '{action}'")
        return

    # Build email context
    email_context = {
        'site_name': getattr(settings, 'SITE_NAME', 'Django App'),
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
    }

    # Add user to context if provided
    if user:
        email_context['user'] = user

    # Merge with provided context
    email_context.update(context)

    # Send email
    try:
        result = EmailService.send_template_email(
            to_email=recipient,
            template_name=template_name,
            context=email_context,
            subject=subject,
        )

        if result.get('success'):
            logger.info(f"Email sent successfully for action '{action}' to {recipient}")
        else:
            logger.error(f"Failed to send email for action '{action}' to {recipient}: {result.get('error')}")

    except Exception as e:
        logger.exception(f"Exception sending email for action '{action}' to {recipient}: {str(e)}")
