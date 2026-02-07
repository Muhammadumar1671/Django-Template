"""Authentication service layer."""

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from datetime import timedelta
import secrets
from apps.authentication.models import PasswordResetToken, EmailVerificationToken

User = get_user_model()


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    @transaction.atomic
    def register_user(email, password, first_name='', last_name=''):
        """
        Register a new user.

        If AUTO_VERIFY_USERS is True in settings, the user will be automatically
        verified without needing to confirm their email.
        """
        # Check if auto-verify is enabled
        auto_verify = getattr(settings, 'AUTO_VERIFY_USERS', False)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_verified=auto_verify  # Auto-verify if enabled
        )

        # Create email verification token (even if auto-verified, for record keeping)
        token = AuthService.create_verification_token(user)

        # If auto-verified, mark token as used
        if auto_verify:
            token.is_used = True
            token.save()

        return user, token
    
    @staticmethod
    def create_verification_token(user):
        """Create email verification token."""
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        
        verification_token = EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        return verification_token
    
    @staticmethod
    @transaction.atomic
    def verify_email(token):
        """Verify user email with token."""
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            
            if not verification_token.is_valid():
                return False, 'Token is invalid or expired'
            
            user = verification_token.user
            user.is_verified = True
            user.save()
            
            verification_token.is_used = True
            verification_token.save()
            
            return True, 'Email verified successfully'
        
        except EmailVerificationToken.DoesNotExist:
            return False, 'Invalid token'
    
    @staticmethod
    def create_password_reset_token(email):
        """Create password reset token."""
        try:
            user = User.objects.get(email=email)
            
            # Invalidate old tokens
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)
            
            # Create new token
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(hours=1)
            
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            return reset_token
        
        except User.DoesNotExist:
            # Don't reveal if email exists
            return None
    
    @staticmethod
    @transaction.atomic
    def reset_password(token, new_password):
        """Reset password with token."""
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return False, 'Token is invalid or expired'
            
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            reset_token.is_used = True
            reset_token.save()
            
            # Invalidate all other reset tokens
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)
            
            return True, 'Password reset successfully'
        
        except PasswordResetToken.DoesNotExist:
            return False, 'Invalid token'
    
    @staticmethod
    @transaction.atomic
    def change_password(user, old_password, new_password):
        """Change user password."""
        if not user.check_password(old_password):
            return False, 'Old password is incorrect'
        
        user.set_password(new_password)
        user.save()
        
        return True, 'Password changed successfully'
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
