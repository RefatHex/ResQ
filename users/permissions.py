# users/permissions.py
from rest_framework import permissions

class IsSameUserOrAdmin(permissions.BasePermission):
    """
    Allow access only to the same user or admin users.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is admin
        if request.user.is_staff:
            return True
        # Allow if the object has a user field that matches the request user
        return obj.user == request.user

class IsCitizen(permissions.BasePermission):
    """
    Allow access only to users with role CITIZEN.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'CITIZEN'

class IsEmergencyService(permissions.BasePermission):
    """
    Allow access only to emergency service users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']

class IsFireStation(permissions.BasePermission):
    """
    Allow access only to fire station users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'FIRE_STATION'

class IsPolice(permissions.BasePermission):
    """
    Allow access only to police users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'POLICE'

class IsRedCrescent(permissions.BasePermission):
    """
    Allow access only to red crescent users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'RED_CRESCENT'