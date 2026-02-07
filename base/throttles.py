"""
Rate limiting throttles for Django REST Framework ViewSets.

These throttle classes provide granular rate limiting for CRUD operations.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
import hashlib


class CRUDBaseThrottle:
    """Base throttle class with common utilities."""

    def get_cache_key(self, request, view):
        """Generate cache key based on user or IP."""
        if request.user and request.user.is_authenticated:
            ident = str(request.user.id)
        else:
            ident = self.get_ident(request)

        # Hash for privacy
        hashed = hashlib.sha256(ident.encode()).hexdigest()[:16]
        return self.cache_format % {
            'scope': self.scope,
            'ident': hashed
        }


class CRUDReadThrottle(CRUDBaseThrottle, UserRateThrottle):
    """Throttle for READ operations (GET, LIST)."""
    scope = 'crud_read'
    rate = '100/minute'


class CRUDWriteThrottle(CRUDBaseThrottle, UserRateThrottle):
    """Throttle for WRITE operations (POST, PUT, PATCH, DELETE)."""
    scope = 'crud_write'
    rate = '50/minute'


class CRUDCreateThrottle(CRUDBaseThrottle, UserRateThrottle):
    """Throttle specifically for CREATE operations (POST)."""
    scope = 'crud_create'
    rate = '30/minute'


class CRUDDeleteThrottle(CRUDBaseThrottle, UserRateThrottle):
    """Throttle specifically for DELETE operations."""
    scope = 'crud_delete'
    rate = '20/minute'


class CRUDAnonThrottle(CRUDBaseThrottle, AnonRateThrottle):
    """Throttle for anonymous users."""
    scope = 'crud_anon'
    rate = '20/hour'


class BurstRateThrottle(CRUDBaseThrottle, UserRateThrottle):
    """Short burst throttle (prevents rapid requests)."""
    scope = 'burst'
    rate = '10/second'


class SustainedRateThrottle(CRUDBaseThrottle, UserRateThrottle):
    """Sustained rate throttle (prevents sustained abuse)."""
    scope = 'sustained'
    rate = '1000/day'


# Predefined throttle combinations for common use cases
class StandardCRUDThrottles:
    """Standard rate limiting for CRUD operations."""
    throttle_classes = [BurstRateThrottle, CRUDReadThrottle, CRUDWriteThrottle, SustainedRateThrottle]


class StrictCRUDThrottles:
    """Strict rate limiting for sensitive operations."""
    throttle_classes = [BurstRateThrottle, CRUDCreateThrottle, CRUDDeleteThrottle, SustainedRateThrottle]


class PublicCRUDThrottles:
    """Rate limiting for public APIs (includes anon throttle)."""
    throttle_classes = [CRUDAnonThrottle, BurstRateThrottle, CRUDReadThrottle]


def get_throttles_for_action(action: str):
    """
    Get appropriate throttle classes based on the action.

    Args:
        action: ViewSet action ('list', 'retrieve', 'create', 'update', 'partial_update', 'destroy')

    Returns:
        list: Throttle classes for the action
    """
    read_actions = ['list', 'retrieve']
    write_actions = ['update', 'partial_update']
    create_actions = ['create']
    delete_actions = ['destroy']

    if action in read_actions:
        return [BurstRateThrottle, CRUDReadThrottle, SustainedRateThrottle]
    elif action in create_actions:
        return [BurstRateThrottle, CRUDCreateThrottle, SustainedRateThrottle]
    elif action in delete_actions:
        return [BurstRateThrottle, CRUDDeleteThrottle, SustainedRateThrottle]
    elif action in write_actions:
        return [BurstRateThrottle, CRUDWriteThrottle, SustainedRateThrottle]
    else:
        return [BurstRateThrottle, CRUDWriteThrottle, SustainedRateThrottle]


class DynamicThrottleMixin:
    """
    Mixin to dynamically apply throttles based on action.

    Usage:
        class MyViewSet(DynamicThrottleMixin, viewsets.ModelViewSet):
            ...
    """

    def get_throttles(self):
        """Override to get action-specific throttles."""
        action = self.action
        throttle_classes = get_throttles_for_action(action)
        return [throttle() for throttle in throttle_classes]
