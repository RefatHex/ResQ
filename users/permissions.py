# users/permissions.py
from rest_framework.permissions import BasePermission

class IsCitizen(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "CITIZEN"

class IsFireStation(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "FIRE_STATION"

class IsPolice(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "POLICE"

class IsRedCrescent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "RED_CRESCENT"

# Example: Allow only admins or the user themselves to edit their profile
class IsSameUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user