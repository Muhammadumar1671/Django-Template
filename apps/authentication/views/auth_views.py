"""Authentication views using class-based structure."""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from apps.authentication.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
)
from apps.authentication.services import AuthService
from apps.email_service.services import EmailService

User = get_user_model()


class RegisterView(APIView):
    """
    Register a new user.

    POST /api/auth/register/
    {
        "email": "user@example.com",
        "password": "securepass123",
        "password_confirm": "securepass123",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user, verification_token = AuthService.register_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', '')
            )

            # Send verification email
            EmailService.send_verification_email(user, verification_token.token)

            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Login user and return JWT tokens.

    POST /api/auth/login/
    {
        "email": "user@example.com",
        "password": "securepass123"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout user by blacklisting refresh token.

    POST /api/auth/logout/
    {
        "refresh": "refresh_token_here"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """
    Get current authenticated user.

    GET /api/auth/me/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    """
    Change user password.

    POST /api/auth/change-password/
    {
        "old_password": "oldpass123",
        "new_password": "newpass123",
        "new_password_confirm": "newpass123"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            success, message = AuthService.change_password(
                user=request.user,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password']
            )

            if success:
                return Response({'message': message}, status=status.HTTP_200_OK)
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """
    Request password reset.

    POST /api/auth/forgot-password/
    {
        "email": "user@example.com"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            reset_token = AuthService.create_password_reset_token(email)

            if reset_token:
                # Send password reset email
                EmailService.send_password_reset_email(reset_token.user, reset_token.token)

            # Always return success to prevent email enumeration
            return Response({
                'message': 'If the email exists, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    Reset password with token.

    POST /api/auth/reset-password/
    {
        "token": "reset_token_here",
        "new_password": "newpass123",
        "new_password_confirm": "newpass123"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            success, message = AuthService.reset_password(
                token=serializer.validated_data['token'],
                new_password=serializer.validated_data['new_password']
            )

            if success:
                return Response({'message': message}, status=status.HTTP_200_OK)
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    Verify email with token.

    POST /api/auth/verify-email/
    {
        "token": "verification_token_here"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            success, message = AuthService.verify_email(
                token=serializer.validated_data['token']
            )

            if success:
                return Response({'message': message}, status=status.HTTP_200_OK)
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    """
    Resend email verification.

    POST /api/auth/resend-verification/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_verified:
            return Response({
                'message': 'Email is already verified'
            }, status=status.HTTP_400_BAD_REQUEST)

        verification_token = AuthService.create_verification_token(user)
        EmailService.send_verification_email(user, verification_token.token)

        return Response({
            'message': 'Verification email sent'
        }, status=status.HTTP_200_OK)
