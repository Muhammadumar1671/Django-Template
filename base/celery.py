"""
Celery configuration for Django project.

This module sets up Celery for async task processing.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')

app = Celery('base')

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')


# Optional: Configure periodic tasks (Celery Beat)
app.conf.beat_schedule = {
    # Example: Clean up old email logs every day at midnight
    'cleanup-old-email-logs': {
        'task': 'apps.email_service.tasks.cleanup_old_email_logs',
        'schedule': crontab(hour=0, minute=0),
    },
}
