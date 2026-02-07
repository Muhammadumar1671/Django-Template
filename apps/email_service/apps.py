"""App configuration for email_service."""

from django.apps import AppConfig


class EmailServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.email_service'
    label = 'email_service'
    verbose_name = 'Email Service'

    def ready(self):
        """Import signal receivers when app is ready."""
        import apps.email_service.receivers  # noqa
