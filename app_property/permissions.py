from rest_framework import permissions

class IsLandlordOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.status == 'active' or (request.user.is_authenticated and (request.user.is_superuser or obj.owner == request.user))
        return (
            request.user.is_authenticated and (
                request.user.is_superuser or obj.owner == request.user)
        )
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == "landlord")
