from rest_framework import permissions
from .models import Booking


class IsTenantOrLandlordOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Booking):
        if request.user.is_superuser:
            return True
        if obj.tenant == request.user:
            return True
        if obj.property.owner == request.user:
            return True
        return False


class IsUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'
