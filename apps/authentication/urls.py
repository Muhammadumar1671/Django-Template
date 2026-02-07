"""URL configuration for authentication app."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.views import (
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

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User
    path('me/', CurrentUserView.as_view(), name='current_user'),

    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Email verification
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
]
