"""Admin configuration for email_service."""

from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.email_service.models import EmailLog, EmailTemplate


@admin.register(EmailLog)
class EmailLogAdmin(ModelAdmin):
    """Admin for EmailLog model."""
    
    list_display = ['to_email', 'subject', 'status', 'provider', 'sent_at', 'created_at']
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['to_email', 'subject', 'provider_message_id']
    ordering = ['-created_at']
    readonly_fields = ['provider_message_id', 'sent_at', 'created_at']
    
    fieldsets = (
        ('Email Details', {
            'fields': ('to_email', 'from_email', 'subject', 'template_name')
        }),
        ('Status', {
            'fields': ('status', 'provider', 'provider_message_id', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'created_at')
        }),
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(ModelAdmin):
    """Admin for EmailTemplate model."""

    list_display = ['name', 'subject', 'is_active', 'updated_at', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'subject', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'html_content', 'text_content'),
            'description': 'Use {{variable}} syntax for dynamic content. Example: {{user.first_name}}, {{verification_url}}'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make name readonly after creation to prevent breaking email references."""
        if obj:
            return self.readonly_fields + ['name']
        return self.readonly_fields
