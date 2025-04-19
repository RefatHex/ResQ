from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
import math
from django.db.models import F, Func

from .models import EmergencyReport, EmergencyTag
from .serializers import EmergencyReportSerializer, EmergencyTagSerializer
from location.models import Location
from location.serializers import LocationSerializer
from users.permissions import IsCitizen, IsFireStation, IsPolice, IsRedCrescent
from notifications.models import Notification
from users.models import User

class EmergencyTagViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    API endpoint for emergency tags (read-only).
    Uses mixins for better structure.
    """
    queryset = EmergencyTag.objects.all()
    serializer_class = EmergencyTagSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmergencyReportViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    """
    API endpoint for emergency reports with mixins for better organization.
    """
    serializer_class = EmergencyReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_emergency', 'reporter_type']
    search_fields = ['description']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_permissions(self):
        """
        - Creating reports: Any authenticated user
        - Viewing reports: Any authenticated user
        - Updating/Deleting: Only the creator, admin, or emergency services
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, 
                                 permissions.IsAdminUser | 
                                 IsFireStation | 
                                 IsPolice | 
                                 IsRedCrescent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        - Admin and emergency services can see all reports
        - Citizens can only see public reports or their own reports
        """
        user = self.request.user
        if user.is_staff or user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']:
            return EmergencyReport.objects.all()
        # Regular citizens can see their own reports and reports marked as public
        return EmergencyReport.objects.filter(reporter=user)
    
    def perform_create(self, serializer):
        # Automatically set the current user as the reporter
        serializer.save(reporter=self.request.user)
    
    @action(detail=False, methods=['post'])
    def report_emergency(self, request):
        """
        Submit an emergency report with current location.
        This endpoint creates both a location entry and an emergency report.
        """
        # First, create or update location
        location_data = request.data.get('location')
        if not location_data:
            return Response({"detail": "Location data is required"}, 
                           status=status.HTTP_400_BAD_REQUEST)
            
        location_serializer = LocationSerializer(data=location_data)
        if location_serializer.is_valid():
            location = location_serializer.save(user=request.user)
            
            # Now create emergency report with this location
            report_data = {
                'reporter_type': request.data.get('reporter_type', 'SPECTATOR'),
                'description': request.data.get('description', ''),
                'location': location.id,
                'is_emergency': True,
                'tags': request.data.get('tags', [])
            }
            
            report_serializer = self.get_serializer(data=report_data)
            if report_serializer.is_valid():
                report = report_serializer.save(reporter=request.user)
                
                # Send notifications to nearby users
                self._notify_nearby_users(report)
                
                return Response(report_serializer.data, status=status.HTTP_201_CREATED)
            return Response(report_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _notify_nearby_users(self, report):
        """Send notifications to users within a certain radius of the emergency"""
        # Default notification radius in kilometers
        radius_km = 5.0
        
        # Get the emergency location
        report_lat = report.latitude
        report_lng = report.longitude
        
        # Skip if no valid location
        if report_lat is None or report_lng is None:
            return
        
        # Find all users with recent locations within the radius
        # This uses the same Haversine formula as in NearbyEmergenciesView
        nearby_users = []
        
        # Get all users with location data
        locations = Location.objects.filter(is_current=True).exclude(user=report.reporter)
        
        for location in locations:
            user_lat = location.latitude
            user_lng = location.longitude
            
            # Skip if no valid coordinates
            if user_lat is None or user_lng is None:
                continue
                
            # Haversine formula
            R = 6371  # Earth radius in kilometers
            dlat = math.radians(user_lat - report_lat)
            dlng = math.radians(user_lng - report_lng)
            a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                 math.cos(math.radians(report_lat)) * math.cos(math.radians(user_lat)) * 
                 math.sin(dlng/2) * math.sin(dlng/2))
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            if distance <= radius_km:
                nearby_users.append({
                    'user': location.user,
                    'distance': distance
                })
        
        # Create notifications for each nearby user
        for user_info in nearby_users:
            user = user_info['user']
            distance = user_info['distance']
            
            # Create notification
            notification = Notification.objects.create(
                recipient=user,
                title="Emergency Nearby!",
                message=f"Emergency reported {distance:.1f}km from your location: {report.description}",
                emergency_report=report,
                notification_type="EMERGENCY_ALERT"
            )
            
            # Send push notification using our service
            from notifications.services import send_push_notification
            
            try:
                send_push_notification(
                    user_id=user.id,
                    title="Emergency Nearby!",
                    body=f"Emergency reported {distance:.1f}km from your location",
                    data={
                        'notification_id': str(notification.id),
                        'emergency_id': str(report.id),
                        'latitude': report_lat,
                        'longitude': report_lng,
                        'distance': distance
                    }
                )
            except Exception as e:
                # Log the error but don't stop processing other notifications
                print(f"Failed to send push notification to user {user.id}: {str(e)}")
    
    def _notify_status_change(self, report, previous_status):
        """Notify the victim if the status has changed"""
        # Only send notification if reporter is a victim
        if report.reporter_type != 'VICTIM':
            return
            
        # Status change messages
        status_messages = {
            'RESPONDING': f"Emergency services have seen your alert and are responding",
            'ON_SCENE': f"Emergency services have arrived on scene for your emergency",
            'RESOLVED': f"Your emergency has been resolved",
        }
        
        if report.status in status_messages:
            # Create notification for the reporter
            notification = Notification.objects.create(
                recipient=report.reporter,
                title="Emergency Status Update",
                message=status_messages[report.status],
                emergency_report=report,
                notification_type="STATUS_UPDATE"
            )
            
            # Send push notification
            from notifications.services import send_push_notification
            
            try:
                send_push_notification(
                    user_id=report.reporter.id,
                    title="Emergency Status Update",
                    body=status_messages[report.status],
                    data={
                        'notification_id': str(notification.id),
                        'emergency_id': str(report.id),
                        'old_status': previous_status,
                        'new_status': report.status
                    }
                )
            except Exception as e:
                # Log error but continue processing
                print(f"Failed to send status notification to user {report.reporter.id}: {str(e)}")
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of an emergency report (for emergency services)"""
        report = self.get_object()
        
        # Only emergency services or admin can update status
        if not (request.user.is_staff or request.user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']):
            return Response({"detail": "You don't have permission to update status"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        status_value = request.data.get('status')
        if not status_value:
            return Response({"detail": "Status value is required"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status value against choices
        valid_statuses = [status[0] for status in EmergencyReport.STATUS_CHOICES]
        if status_value not in valid_statuses:
            return Response(
                {"detail": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Store previous status for notification
        previous_status = report.status
        
        # Update the status
        report.status = status_value
        report.save()
        
        # Send notification if status changed
        if previous_status != status_value:
            self._notify_status_change(report, previous_status)
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)

class NearbyEmergenciesView(generics.ListAPIView):
    """
    List emergencies within a certain radius of provided coordinates.
    Used by emergency services to find nearby incidents.
    """
    serializer_class = EmergencyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only staff and emergency services can use this endpoint
        user = self.request.user
        if not (user.is_staff or user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']):
            return EmergencyReport.objects.none()
        
        # Get parameters from request
        latitude = self.request.query_params.get('lat')
        longitude = self.request.query_params.get('lng')
        radius_km = float(self.request.query_params.get('radius', 5))
        
        if not (latitude and longitude):
            return EmergencyReport.objects.none()
        
        # Convert string parameters to float
        lat = float(latitude)
        lng = float(longitude)
        
        # Get all emergency reports
        queryset = EmergencyReport.objects.filter(is_emergency=True, status='PENDING')
        
        # Filter in Python using Haversine formula
        filtered_reports = []
        for report in queryset:
            # Calculate distance using Haversine formula
            # Access latitude/longitude directly from the model instead of location
            report_lat = report.latitude if report.latitude is not None else 0
            report_lng = report.longitude if report.longitude is not None else 0
            
            # Haversine formula
            R = 6371  # Earth radius in kilometers
            dlat = math.radians(report_lat - lat)
            dlng = math.radians(report_lng - lng)
            a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                 math.cos(math.radians(lat)) * math.cos(math.radians(report_lat)) * 
                 math.sin(dlng/2) * math.sin(dlng/2))
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            if distance <= radius_km:
                # Add distance as attribute to report object
                report.distance = distance
                filtered_reports.append(report)
        
        # Sort by distance
        filtered_reports.sort(key=lambda x: x.distance)
        
        return filtered_reports

class EmergencyStatsByTagView(generics.ListAPIView):
    """Get statistics about emergency reports by tag type"""
    serializer_class = EmergencyTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only available to staff and emergency services
        user = self.request.user
        if not (user.is_staff or user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']):
            return EmergencyTag.objects.none()
        
        return EmergencyTag.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        
        for tag in queryset:
            # Count reports with this tag
            report_count = tag.reports.count()
            data.append({
                'id': tag.id,
                'name': tag.name,
                'emergency_type': tag.emergency_type,
                'count': report_count
            })
            
        return Response(data)
