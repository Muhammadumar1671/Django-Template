"""
Generic email signals for triggering emails on various actions.

This module provides a single, generic signal that can be used to send emails
for any action in the application. No need to create multiple signals.

Usage:
    from apps.email_service.signals import send_email_signal

    # Trigger an email
    send_email_signal.send(
        sender=YourModel,
        action='user_registered',  # Action name
        recipient=user.email,      # Recipient email
        user=user,                 # User object (optional)
        context={                  # Additional context for template
            'verification_url': 'https://...',
            'custom_data': 'value'
        }
    )

Available default actions:
    - user_registered: Sends verification email
    - password_reset: Sends password reset email
    - email_verified: Sends welcome email
    - password_changed: Sends password change confirmation
    - custom: Send custom email (requires template_name and subject in context)
"""

import django.dispatch


# Generic signal for all email actions
send_email_signal = django.dispatch.Signal()


def get_email_config_for_action(action: str) -> dict:
    """
    Get email configuration for a specific action.

    Returns:
        dict: {
            'template_name': str,  # Template identifier or path
            'subject': str,        # Email subject (optional if using DB template)
            'enabled': bool        # Whether this action should trigger email
        }
    """
    configs = {
        'user_registered': {
            'template_name': 'emails/verify_email.html',
            'subject': 'Verify your email address',
            'enabled': True,
        },
        'password_reset': {
            'template_name': 'emails/password_reset.html',
            'subject': 'Reset your password',
            'enabled': True,
        },
        'email_verified': {
            'template_name': 'emails/welcome.html',
            'subject': 'Welcome to our platform!',
            'enabled': True,
        },
        'password_changed': {
            'template_name': 'emails/password_changed.html',
            'subject': 'Your password was changed',
            'enabled': True,
        },
        # Custom action - requires template_name and subject in signal context
        'custom': {
            'template_name': None,
            'subject': None,
            'enabled': True,
        },
    }

    return configs.get(action, {
        'template_name': None,
        'subject': None,
        'enabled': False,
    })
