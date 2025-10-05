from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.created_by or request.user.is_superuser

class IsAgentOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['agent'] or request.user.is_superuser
