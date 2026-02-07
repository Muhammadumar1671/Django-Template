"""
Rate limiting utilities for authentication endpoints.

Provides decorators and utilities to prevent brute-force attacks and spam.
"""

from functools import wraps
from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from typing import Callable, Optional
import hashlib
import time


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


def get_client_ip(request) -> str:
    """
    Get client IP address from request.

    Args:
        request: Django request object

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_rate_limit_key(identifier: str, action: str) -> str:
    """
    Generate a cache key for rate limiting.

    Args:
        identifier: Unique identifier (IP, user ID, email, etc.)
        action: Action being rate limited

    Returns:
        str: Cache key
    """
    # Hash the identifier for privacy
    hashed = hashlib.sha256(identifier.encode()).hexdigest()[:16]
    return f"ratelimit:{action}:{hashed}"


def is_rate_limited(
    identifier: str,
    action: str,
    limit: int,
    period: int,
    increment: bool = True
) -> tuple[bool, Optional[int]]:
    """
    Check if an action is rate limited.

    Args:
        identifier: Unique identifier (IP, user ID, email, etc.)
        action: Action being rate limited
        limit: Maximum number of requests
        period: Time period in seconds
        increment: Whether to increment the counter

    Returns:
        tuple: (is_limited, retry_after_seconds)
    """
    cache_key = get_rate_limit_key(identifier, action)

    # Get current count
    current_count = cache.get(cache_key, 0)

    if current_count >= limit:
        # Get TTL to inform user when they can retry
        ttl = cache.ttl(cache_key)
        return True, max(ttl, 1) if ttl else period

    if increment:
        # Increment counter
        if current_count == 0:
            # First request, set with expiry
            cache.set(cache_key, 1, period)
        else:
            # Increment existing counter
            cache.incr(cache_key)

    return False, None


def ratelimit(
    key: str = 'ip',
    rate: str = '5/m',
    method: str = 'ALL',
    block: bool = True
):
    """
    Decorator for rate limiting views.

    Args:
        key: What to use as identifier ('ip', 'user', 'email', or callable)
        rate: Rate limit (e.g., '5/m' = 5 per minute, '10/h' = 10 per hour)
        method: HTTP method to limit ('ALL', 'POST', 'GET', etc.)
        block: Whether to block request or just flag it

    Example:
        @ratelimit(key='ip', rate='5/m', method='POST')
        def my_view(request):
            ...

        @ratelimit(key='email', rate='3/h', method='POST')
        def forgot_password(request):
            ...
    """
    def decorator(view_func: Callable):
        @wraps(view_func)
        def wrapped_view(view_instance, request, *args, **kwargs):
            # Parse rate string
            limit, period_str = rate.split('/')
            limit = int(limit)

            # Convert period to seconds
            period_map = {
                's': 1,
                'm': 60,
                'h': 3600,
                'd': 86400,
            }
            period = period_map.get(period_str.lower(), 60)

            # Check if method matches
            if method != 'ALL' and request.method != method.upper():
                return view_func(view_instance, request, *args, **kwargs)

            # Get identifier based on key type
            if key == 'ip':
                identifier = get_client_ip(request)
            elif key == 'user':
                if request.user.is_authenticated:
                    identifier = str(request.user.id)
                else:
                    identifier = get_client_ip(request)
            elif key == 'email':
                # Get email from request data
                email = request.data.get('email', '')
                identifier = email if email else get_client_ip(request)
            elif callable(key):
                identifier = key(view_instance, request)
            else:
                identifier = get_client_ip(request)

            # Get action name (view name + method)
            action = f"{view_func.__name__}:{request.method}"

            # Check rate limit
            is_limited, retry_after = is_rate_limited(
                identifier=identifier,
                action=action,
                limit=limit,
                period=period,
                increment=True
            )

            if is_limited and block:
                return Response({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': retry_after
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Add rate limit info to request
            request.rate_limited = is_limited

            return view_func(view_instance, request, *args, **kwargs)

        return wrapped_view
    return decorator


class RateLimitMixin:
    """
    Mixin for class-based views to add rate limiting.

    Usage:
        class MyView(RateLimitMixin, APIView):
            ratelimit_key = 'ip'
            ratelimit_rate = '5/m'
            ratelimit_method = 'POST'
            ratelimit_block = True
    """

    ratelimit_key: str = 'ip'
    ratelimit_rate: str = '10/m'
    ratelimit_method: str = 'ALL'
    ratelimit_block: bool = True

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add rate limiting."""
        # Parse rate string
        limit, period_str = self.ratelimit_rate.split('/')
        limit = int(limit)

        # Convert period to seconds
        period_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        period = period_map.get(period_str.lower(), 60)

        # Check if method matches
        if self.ratelimit_method != 'ALL' and request.method != self.ratelimit_method.upper():
            return super().dispatch(request, *args, **kwargs)

        # Get identifier
        if self.ratelimit_key == 'ip':
            identifier = get_client_ip(request)
        elif self.ratelimit_key == 'user':
            identifier = str(request.user.id) if request.user.is_authenticated else get_client_ip(request)
        elif self.ratelimit_key == 'email':
            email = request.data.get('email', '')
            identifier = email if email else get_client_ip(request)
        else:
            identifier = get_client_ip(request)

        # Get action name
        action = f"{self.__class__.__name__}:{request.method}"

        # Check rate limit
        is_limited, retry_after = is_rate_limited(
            identifier=identifier,
            action=action,
            limit=limit,
            period=period,
            increment=True
        )

        if is_limited and self.ratelimit_block:
            return Response({
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': retry_after
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Add rate limit info to request
        request.rate_limited = is_limited

        return super().dispatch(request, *args, **kwargs)


# Predefined rate limit configurations
class RateLimitConfig:
    """Common rate limit configurations."""

    # Authentication endpoints
    LOGIN = {'key': 'ip', 'rate': '5/m', 'method': 'POST'}
    REGISTER = {'key': 'ip', 'rate': '3/h', 'method': 'POST'}
    FORGOT_PASSWORD = {'key': 'email', 'rate': '3/h', 'method': 'POST'}
    RESET_PASSWORD = {'key': 'ip', 'rate': '5/h', 'method': 'POST'}
    VERIFY_EMAIL = {'key': 'ip', 'rate': '10/h', 'method': 'POST'}
    RESEND_VERIFICATION = {'key': 'user', 'rate': '3/h', 'method': 'POST'}

    # API endpoints
    API_READ = {'key': 'user', 'rate': '100/m', 'method': 'GET'}
    API_WRITE = {'key': 'user', 'rate': '50/m', 'method': 'POST'}
