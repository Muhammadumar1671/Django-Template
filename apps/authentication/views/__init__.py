"""Authentication views."""

from .auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
    VerifyEmailView,
    ResendVerificationView,
)

__all__ = [
    'RegisterView',
    'LoginView',
    'LogoutView',
    'CurrentUserView',
    'ChangePasswordView',
    'ForgotPasswordView',
    'ResetPasswordView',
    'VerifyEmailView',
    'ResendVerificationView',
]
