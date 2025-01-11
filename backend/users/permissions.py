from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        return obj == request.user or request.user.is_staff

class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow farmers to perform certain actions.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'farmer'

class IsConsumer(permissions.BasePermission):
    """
    Custom permission to only allow consumers to perform certain actions.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'consumer'
