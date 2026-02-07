"""Admin configuration for authentication app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from apps.authentication.models import User, PasswordResetToken, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Admin for User model."""
    
    list_display = ['email', 'first_name', 'last_name', 'is_verified', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'is_verified', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(ModelAdmin):
    """Admin for PasswordResetToken model."""
    
    list_display = ['user', 'is_used', 'expires_at', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    ordering = ['-created_at']
    readonly_fields = ['token', 'created_at']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(ModelAdmin):
    """Admin for EmailVerificationToken model."""
    
    list_display = ['user', 'is_used', 'expires_at', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    ordering = ['-created_at']
    readonly_fields = ['token', 'created_at']
