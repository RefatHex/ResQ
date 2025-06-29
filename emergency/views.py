from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
import math
from django.db.models import F, Func
import logging

from .models import EmergencyReport, EmergencyTag
from .serializers import EmergencyReportSerializer, EmergencyTagSerializer
from users.permissions import IsCitizen, IsFireStation, IsPolice, IsRedCrescent
from notifications.models import Notification
from users.models import User
from social.views import post_emergency_to_social_media

# Set up logger
logger = logging.getLogger(__name__)

class EmergencyTagViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    API endpoint for emergency tags
    """
    queryset = EmergencyTag.objects.all()
    serializer_class = EmergencyTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about emergency tags usage"""
        tags_with_counts = EmergencyTag.objects.annotate(
            count=Func(F('emergencyreport'), function='COUNT')
        ).values('id', 'name', 'emergency_type', 'count')
        
        return Response(tags_with_counts)

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
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'update_status':
            permission_classes = [permissions.IsAuthenticated, IsFireStation | IsPolice | IsRedCrescent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return different querysets based on user role:
        - Admin and emergency services: all reports
        - Regular users: only their own reports
        """
        user = self.request.user
        if user.is_staff or user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']:
            return EmergencyReport.objects.all().select_related('reporter').prefetch_related('tags')
        return EmergencyReport.objects.filter(reporter=user).select_related('reporter').prefetch_related('tags')
    
    def perform_create(self, serializer):
        """
        Automatically set the current user as the reporter
        """
        logger.debug(f"Creating emergency report with serializer data: {serializer.validated_data}")
        serializer.save(reporter=self.request.user)
    
    def perform_create_and_get_instance(self, serializer):
        """
        Same as perform_create but returns the created instance
        """
        logger.debug(f"Creating emergency report with serializer data: {serializer.validated_data}")
        return serializer.save(reporter=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a standard emergency report with detailed logging for debugging"""
        logger.debug("=== EmergencyReportViewSet.create Request ===")
        logger.debug(f"Request Data: {request.data}")
        logger.debug(f"Content Type: {request.content_type}")
        logger.debug(f"Request Headers: {request.headers}")
        
        # Print raw request data to console for immediate debugging
        print("\n=== EmergencyReportViewSet.create Request ===")
        print(f"Request Data: {request.data}")
        print(f"Content Type: {request.content_type}")
        print(f"Request Headers: {request.headers}")
        print("========================================\n")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            report = self.perform_create_and_get_instance(serializer)
            
            # Post to social media if it's an emergency
            if report.is_emergency:
                # Prepare additional emergency info from request
                emergency_data = {
                    'description': report.description,
                    'emergency_type': request.data.get('incident_type', 'General Emergency'),
                    'contact_info': request.data.get('contact_info', ''),
                    'severity': request.data.get('severity', ''),
                    'people_count': request.data.get('people_count', '')
                }
                
                # Create location data from latitude and longitude
                location_data = None
                if report.latitude is not None and report.longitude is not None:
                    location_data = {
                        'latitude': report.latitude,
                        'longitude': report.longitude
                    }
                
                try:
                    social_results = post_emergency_to_social_media(
                        emergency_data,
                        location_data,
                        request.data.get('media_file')
                    )
                    
                    # Add social media results to response
                    response_data = serializer.data
                    if social_results and social_results.get('success'):
                        response_data['social_post_results'] = social_results.get('results', [])
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
                except Exception as e:
                    logger.error(f"Error posting to social media: {str(e)}")
                    # Continue with the standard response even if social media posting fails
        
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            # Log validation errors
            logger.error(f"Serializer validation errors: {serializer.errors}")
            print("\n=== Serializer Errors ===")
            print(f"Errors: {serializer.errors}")
            print("=========================\n")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def report_emergency(self, request):
        """
        Custom action for reporting emergencies
        """
        try:
            # Print raw request data for debugging
            print(f"EMERGENCY REPORT REQUEST DATA: {request.data}")
            
            # Extract coordinates from request
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            
            if not latitude or not longitude:
                return Response(
                    {'error': 'Latitude and longitude are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare report data
            report_data = {
                'description': request.data.get('description'),
                'reporter_type': request.data.get('reporter_type', 'SPECTATOR'),
                'is_emergency': True,
                'latitude': latitude,
                'longitude': longitude,
                'tag_ids': request.data.get('tag_ids', [])
            }
            
            # Create emergency report
            report_serializer = self.get_serializer(data=report_data)
            if report_serializer.is_valid():
                report = report_serializer.save(reporter=request.user)
                
                # Prepare additional emergency info from request
                emergency_data = {
                    'description': report.description,
                    'emergency_type': request.data.get('incident_type', 'General Emergency'),
                    'contact_info': request.data.get('contact_info', ''),
                    'severity': request.data.get('severity', ''),
                    'people_count': request.data.get('people_count', '')
                }
                
                # Create location data from latitude and longitude
                location_data = None
                if report.latitude is not None and report.longitude is not None:
                    location_data = {
                        'latitude': report.latitude,
                        'longitude': report.longitude
                    }
                
                # Attempt to post to social media if media file is included
                social_results = {}
                try:
                    social_results = post_emergency_to_social_media(
                        emergency_data,
                        location_data,
                        request.data.get('media_file')
                    )
                except Exception as e:
                    logger.error(f"Error posting to social media: {str(e)}")
                
                # Include social media results in the response
                response_data = report_serializer.data
                if social_results and social_results.get('success'):
                    response_data['social_post_results'] = social_results.get('results', [])
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            return Response(report_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.exception("Error in report_emergency")
            return Response(
                {'error': f'Failed to create emergency report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of an emergency report (for emergency services)
        """
        report = self.get_object()
        old_status = report.status
        
        status_value = request.data.get('status')
        if not status_value:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if status is valid
        valid_statuses = ['PENDING', 'RESPONDING', 'ON_SCENE', 'RESOLVED']
        if status_value not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.status = status_value
        report.save()
        
        # Create notification for the reporter
        if report.reporter.id != request.user.id:
            Notification.objects.create(
                recipient=report.reporter,
                title='Emergency Status Update',
                message=f'Your emergency report has been updated to {report.get_status_display()}',
                notification_type='UPDATE'
            )
        
        # Return updated report
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def multi_location(self, request):
        """
        Report an emergency affecting multiple locations (e.g., wildfire)
        """
        try:
            # Validate request data
            if not request.data.get('locations') or not isinstance(request.data.get('locations'), list):
                return Response(
                    {'error': 'At least one location is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create main report from the first location
            first_location = request.data.get('locations')[0]
            report_data = {
                'description': request.data.get('description'),
                'reporter_type': request.data.get('reporter_type', 'SPECTATOR'),
                'is_emergency': request.data.get('is_emergency', True),
                'latitude': first_location.get('latitude'),
                'longitude': first_location.get('longitude'),
                'tag_ids': request.data.get('tag_ids', [])
            }
            
            # Create emergency report
            report_serializer = self.get_serializer(data=report_data)
            if report_serializer.is_valid():
                main_report = report_serializer.save(reporter=request.user)
                
                # Create additional reports for other locations
                additional_reports = []
                for location_data in request.data.get('locations')[1:]:
                    additional_report_data = {
                        'description': request.data.get('description'),
                        'reporter_type': request.data.get('reporter_type', 'SPECTATOR'),
                        'is_emergency': request.data.get('is_emergency', True),
                        'latitude': location_data.get('latitude'),
                        'longitude': location_data.get('longitude'),
                        'tag_ids': request.data.get('tag_ids', [])
                    }
                    additional_report_serializer = self.get_serializer(data=additional_report_data)
                    if additional_report_serializer.is_valid():
                        additional_report = additional_report_serializer.save(reporter=request.user)
                        additional_reports.append(additional_report_serializer.data)
                
                # Return combined response
                return Response({
                    'main_report': report_serializer.data,
                    'additional_reports': additional_reports,
                    'total_locations': len(request.data.get('locations'))
                }, status=status.HTTP_201_CREATED)
            
            return Response(report_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.exception("Error in multi_location")
            return Response(
                {'error': f'Failed to create multi-location report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NearbyEmergenciesView(generics.ListAPIView):
    """Find emergencies within a specific radius"""
    serializer_class = EmergencyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = float(self.request.query_params.get('radius', 5.0))  # Default 5km
        
        if not lat or not lng:
            return EmergencyReport.objects.none()
        
        lat = float(lat)
        lng = float(lng)
        
        # Get all active emergencies
        active_emergencies = EmergencyReport.objects.filter(
            is_emergency=True,
            status__in=['PENDING', 'RESPONDING', 'ON_SCENE']
        ).select_related('reporter').prefetch_related('tags')
        
        # Calculate distance for each emergency
        emergencies_with_distance = []
        for emergency in active_emergencies:
            distance = self.calculate_distance(
                lat, lng, emergency.latitude, emergency.longitude
            )
            if distance <= radius:
                emergency.distance = distance  # Attach distance for serializer
                emergencies_with_distance.append(emergency)
        
        # Sort by distance
        return sorted(emergencies_with_distance, key=lambda e: e.distance)
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Radius of the Earth in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return round(distance, 2)

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