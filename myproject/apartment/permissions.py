import re
from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.role == 'ADMIN':
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        
        if request.user.role == 'ADMIN':
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'resident'):
            return obj.resident == request.user
        
        return False
    

class IsAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'
    

class IsResident(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'RESIDENT'