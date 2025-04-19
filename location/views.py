from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Location
from .serializers import LocationSerializer
from users.permissions import IsSameUserOrAdmin

class LocationViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    API endpoint for managing user locations.
    Uses mixins for better readability and maintainability.
    """
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameUserOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        # Admin users can see all locations, regular users only see their own
        if user.is_staff:
            return Location.objects.all().order_by('-timestamp')
        return Location.objects.filter(user=user).order_by('-timestamp')
    
    def perform_create(self, serializer):
        # Automatically set the current user
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the user's latest location"""
        location = Location.objects.filter(user=request.user).order_by('-timestamp').first()
        if location:
            serializer = self.get_serializer(location)
            return Response(serializer.data)
        return Response({"detail": "No location found for this user"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def emergency(self, request):
        """Update user location during emergency"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Create new location record with emergency flag
            serializer.save(
                user=request.user,
                is_emergency=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmergencyLocationsListView(generics.ListAPIView):
    """List all emergency locations (for emergency services and admin only)"""
    serializer_class = LocationSerializer
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']:
            return Location.objects.filter(is_emergency=True).order_by('-timestamp')
        # Regular users can only see their own emergency locations
        return Location.objects.filter(user=user, is_emergency=True).order_by('-timestamp')
