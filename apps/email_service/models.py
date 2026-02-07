"""Email service models for tracking sent emails."""

from django.db import models
import uuid


class EmailLog(models.Model):
    """Log of all sent emails."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    to_email = models.EmailField(db_index=True)
    from_email = models.EmailField()
    subject = models.CharField(max_length=255)
    template_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    provider = models.CharField(max_length=50)  # sendgrid, resend, smtp, etc.
    provider_message_id = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['to_email', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} to {self.to_email}"


class EmailTemplate(models.Model):
    """Email templates that can be managed from admin panel."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True, help_text="Template identifier (e.g., 'welcome', 'password_reset')")
    subject = models.CharField(max_length=255, help_text="Email subject line. Use {{variable}} for dynamic content")
    html_content = models.TextField(help_text="HTML email content. Use {{variable}} for dynamic content")
    text_content = models.TextField(blank=True, help_text="Plain text version (optional)")
    description = models.TextField(blank=True, help_text="What this template is used for")
    is_active = models.BooleanField(default=True, help_text="Inactive templates won't be used")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email_templates'
        ordering = ['name']
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'

    def __str__(self):
        return f"{self.name} - {self.subject}"
