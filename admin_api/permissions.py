from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission untuk admin user saja"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin bisa semua, user biasa read-only"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
