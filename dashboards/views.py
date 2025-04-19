from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, F

from emergency.models import EmergencyReport
from notifications.models import Notification
from users.permissions import IsEmergencyService, IsCitizen
from users.models import User

class DashboardBaseView(APIView):
    """Base view for dashboards with common data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_common_data(self, request):
        """Get data common to all dashboard types"""
        user = request.user
        
        # Recent notifications
        recent_notifications = Notification.objects.filter(
            recipient=user
        ).order_by('-timestamp')[:5]
        
        # Unread notification count
        unread_count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
        
        # User profile completeness - simple implementation
        profile_fields = ['first_name', 'last_name', 'email', 'phone_number', 'role']
        completed_fields = sum(1 for field in profile_fields if getattr(user, field))
        profile_completeness = round((completed_fields / len(profile_fields)) * 100)
        
        return {
            'username': user.username,
            'role': user.role,
            'recent_notifications': [
                {
                    'id': n.id,
                    'title': n.title,
                    'message': n.message,
                    'timestamp': n.timestamp,
                    'is_read': n.is_read
                } for n in recent_notifications
            ],
            'unread_notifications': unread_count,
            'profile_completeness': profile_completeness
        }

class CitizenDashboardView(DashboardBaseView):
    """Dashboard view for regular citizens"""
    permission_classes = [permissions.IsAuthenticated, IsCitizen]
    
    def get(self, request):
        # Get common dashboard data
        data = self.get_common_data(request)
        
        # Get citizen-specific data
        user = request.user
        
        # Recent emergency reports by this user
        recent_reports = EmergencyReport.objects.filter(
            reporter=user
        ).order_by('-timestamp')[:5]
        
        # Ongoing emergencies reported by this user
        ongoing_emergencies = EmergencyReport.objects.filter(
            reporter=user,
            status__in=['PENDING', 'RESPONDING', 'ON_SCENE']
        ).count()
        
        # Add citizen-specific data
        data.update({
            'recent_reports': [
                {
                    'id': r.id,
                    'description': r.description,
                    'status': r.status,
                    'timestamp': r.timestamp,
                    'reporter_type': r.reporter_type
                } for r in recent_reports
            ],
            'ongoing_emergencies': ongoing_emergencies,
            'total_reports': EmergencyReport.objects.filter(reporter=user).count(),
            'resolved_reports': EmergencyReport.objects.filter(
                reporter=user, 
                status='RESOLVED'
            ).count()
        })
        
        return Response(data)

class EmergencyServiceDashboardView(DashboardBaseView):
    """Dashboard view for emergency services (fire, police, red crescent)"""
    permission_classes = [permissions.IsAuthenticated, IsEmergencyService]
    
    def get(self, request):
        # Get common dashboard data
        data = self.get_common_data(request)
        
        # Get emergency service specific data
        user = request.user
        user_role = user.role
        
        # Filter emergencies based on the service type (optional)
        # This assumes EmergencyTag has types that match service roles
        role_to_emergency_type = {
            'FIRE_STATION': 'FIRE',
            'POLICE': 'CRIME',
            'RED_CRESCENT': 'MEDICAL'
        }
        
        emergency_type = role_to_emergency_type.get(user_role)
        
        # Recent pending emergencies
        pending_filter = Q(status='PENDING')
        if emergency_type:
            pending_filter &= Q(tags__emergency_type=emergency_type)
            
        pending_emergencies = EmergencyReport.objects.filter(
            pending_filter
        ).order_by('-timestamp')[:10]
        
        # Active emergencies by status
        active = EmergencyReport.objects.filter(
            status__in=['PENDING', 'RESPONDING', 'ON_SCENE']
        )
        
        if emergency_type:
            active = active.filter(tags__emergency_type=emergency_type)
        
        # Counters by status
        status_counts = dict(active.values_list('status').annotate(count=Count('status')))
        
        # Add emergency service specific data
        data.update({
            'pending_emergencies': [
                {
                    'id': e.id,
                    'description': e.description,
                    'status': e.status,
                    'timestamp': e.timestamp,
                    'latitude': e.latitude,
                    'longitude': e.longitude,
                    'is_emergency': e.is_emergency
                } for e in pending_emergencies
            ],
            'current_status': {
                'pending': status_counts.get('PENDING', 0),
                'responding': status_counts.get('RESPONDING', 0),
                'on_scene': status_counts.get('ON_SCENE', 0)
            },
            'service_type': user_role,
            'recent_activity': {
                'today': EmergencyReport.objects.filter(
                    timestamp__date=timezone.now().date(),
                    status='RESOLVED'
                ).count(),
                'this_week': EmergencyReport.objects.filter(
                    timestamp__date__gte=timezone.now().date() - timedelta(days=7),
                    status='RESOLVED'
                ).count()
            }
        })
        
        return Response(data)

class AdminDashboardView(DashboardBaseView):
    """Dashboard view for admin users"""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get(self, request):
        # Get common dashboard data
        data = self.get_common_data(request)
        
        # Get admin-specific data
        
        # System status
        total_users = User.objects.count()
        total_emergencies = EmergencyReport.objects.count()
        pending_emergencies = EmergencyReport.objects.filter(status='PENDING').count()
        resolved_emergencies = EmergencyReport.objects.filter(status='RESOLVED').count()
        
        # Today's statistics
        today = timezone.now().date()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        emergencies_today = EmergencyReport.objects.filter(timestamp__date=today).count()
        
        # Recent emergency reports
        recent_reports = EmergencyReport.objects.all().order_by('-timestamp')[:10]
        
        # Add admin-specific data
        data.update({
            'system_status': {
                'total_users': total_users,
                'total_emergencies': total_emergencies,
                'pending_emergencies': pending_emergencies,
                'resolved_emergencies': resolved_emergencies,
                'resolution_rate': round(resolved_emergencies / total_emergencies * 100, 2) if total_emergencies > 0 else 0
            },
            'today_stats': {
                'new_users': new_users_today,
                'emergencies': emergencies_today
            },
            'recent_reports': [
                {
                    'id': r.id,
                    'description': r.description,
                    'status': r.status,
                    'timestamp': r.timestamp,
                    'reporter': r.reporter.username,
                    'reporter_type': r.reporter_type
                } for r in recent_reports
            ]
        })
        
        return Response(data)
