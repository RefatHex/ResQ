from django.shortcuts import render
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import SystemMetric, RegionalMetric, UserActivity, EmergencyTypeMetric
from emergency.models import EmergencyReport
from users.models import User
from users.permissions import IsEmergencyService

class GlobalAnalyticsView(APIView):
    """Provides system-wide analytics data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Only admins and emergency services can see global analytics
        if not (request.user.is_staff or request.user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']):
            return Response({"detail": "You don't have permission to access global analytics"},
                           status=status.HTTP_403_FORBIDDEN)
        
        # Get date range from request or use default (last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get global metrics
        system_metrics = SystemMetric.objects.filter(date__gte=start_date)
        
        # If no metrics exist, compute them on the fly
        if not system_metrics.exists():
            today = timezone.now().date()
            
            # Calculate metrics for the requested period
            active_users = User.objects.filter(last_login__date__gte=start_date).count()
            new_users = User.objects.filter(date_joined__date__gte=start_date).count()
            emergency_reports = EmergencyReport.objects.filter(timestamp__date__gte=start_date).count()
            resolved_emergencies = EmergencyReport.objects.filter(
                timestamp__date__gte=start_date,
                status='RESOLVED'
            ).count()
            
            # Create a summary of metrics
            data = {
                'period': f'Last {days} days',
                'active_users': active_users,
                'new_users': new_users,
                'emergency_reports': emergency_reports,
                'resolved_emergencies': resolved_emergencies,
                'resolution_rate': round(resolved_emergencies / emergency_reports * 100, 2) if emergency_reports > 0 else 0
            }
        else:
            # Aggregate existing metrics
            aggregated = system_metrics.aggregate(
                active_users_sum=Sum('active_users'),
                new_users_sum=Sum('new_users'),
                emergency_reports_sum=Sum('emergency_reports'),
                resolved_emergencies_sum=Sum('resolved_emergencies')
            )
            
            data = {
                'period': f'Last {days} days',
                'active_users': aggregated['active_users_sum'] or 0,
                'new_users': aggregated['new_users_sum'] or 0,
                'emergency_reports': aggregated['emergency_reports_sum'] or 0,
                'resolved_emergencies': aggregated['resolved_emergencies_sum'] or 0,
                'resolution_rate': round((aggregated['resolved_emergencies_sum'] or 0) / 
                                        (aggregated['emergency_reports_sum'] or 1) * 100, 2)
            }
        
        # Add emergency type breakdown
        emergency_types = EmergencyTypeMetric.objects.filter(date__gte=start_date)
        type_data = {}
        
        if emergency_types.exists():
            for e_type in emergency_types:
                if e_type.emergency_type not in type_data:
                    type_data[e_type.emergency_type] = {
                        'count': 0,
                        'avg_response_time': 0,
                        'resolution_rate': 0
                    }
                
                type_data[e_type.emergency_type]['count'] += e_type.count
                # Average the averages properly
                if type_data[e_type.emergency_type]['avg_response_time'] > 0:
                    type_data[e_type.emergency_type]['avg_response_time'] = (
                        type_data[e_type.emergency_type]['avg_response_time'] + e_type.avg_response_time
                    ) / 2
                else:
                    type_data[e_type.emergency_type]['avg_response_time'] = e_type.avg_response_time
                
                type_data[e_type.emergency_type]['resolution_rate'] = e_type.resolution_rate
        else:
            # Calculate on the fly from emergency reports
            from emergency.models import EmergencyTag
            for tag in EmergencyTag.objects.all():
                reports = EmergencyReport.objects.filter(
                    tags=tag,
                    timestamp__date__gte=start_date
                )
                resolved = reports.filter(status='RESOLVED').count()
                total = reports.count()
                
                if total > 0:
                    type_data[tag.emergency_type] = {
                        'count': total,
                        'resolution_rate': round(resolved / total * 100, 2)
                    }
        
        data['emergency_types'] = type_data
        
        return Response(data)

class RegionalAnalyticsView(APIView):
    """Provides analytics data by region"""
    permission_classes = [permissions.IsAuthenticated, IsEmergencyService]
    
    def get(self, request):
        # Get date range from request or use default (last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get regional metrics
        regional_metrics = RegionalMetric.objects.filter(date__gte=start_date)
        
        # Aggregate by region
        region_data = {}
        for metric in regional_metrics:
            if metric.region not in region_data:
                region_data[metric.region] = {
                    'emergency_count': 0,
                    'response_time_avg': 0
                }
            
            region_data[metric.region]['emergency_count'] += metric.emergency_count
            # Average the averages properly
            if region_data[metric.region]['response_time_avg'] > 0:
                region_data[metric.region]['response_time_avg'] = (
                    region_data[metric.region]['response_time_avg'] + metric.response_time_avg
                ) / 2
            else:
                region_data[metric.region]['response_time_avg'] = metric.response_time_avg
        
        return Response({
            'period': f'Last {days} days',
            'regions': region_data
        })

class UserAnalyticsView(APIView):
    """Provides analytics data for the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get date range from request or use default (last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get user activity
        user_activity = UserActivity.objects.filter(
            user=request.user,
            date__gte=start_date
        )
        
        if user_activity.exists():
            # Aggregate user activity
            aggregated = user_activity.aggregate(
                logins_sum=Sum('logins'),
                reports_sum=Sum('reports_submitted'),
                notifications_sum=Sum('notifications_received')
            )
            
            data = {
                'period': f'Last {days} days',
                'logins': aggregated['logins_sum'] or 0,
                'reports_submitted': aggregated['reports_sum'] or 0,
                'notifications_received': aggregated['notifications_sum'] or 0
            }
        else:
            # Calculate on the fly
            from notifications.models import Notification
            
            reports_count = EmergencyReport.objects.filter(
                reporter=request.user,
                timestamp__date__gte=start_date
            ).count()
            
            notifications_count = Notification.objects.filter(
                recipient=request.user,
                timestamp__date__gte=start_date
            ).count()
            
            data = {
                'period': f'Last {days} days',
                'logins': 1,  # At least the current login
                'reports_submitted': reports_count,
                'notifications_received': notifications_count
            }
        
        # Add emergency response stats for emergency service users
        if request.user.role in ['FIRE_STATION', 'POLICE', 'RED_CRESCENT']:
            # Calculate response metrics specific to their service type
            # This is a placeholder for real logic based on your data model
            data['service_metrics'] = {
                'total_responses': 0,
                'average_response_time': 0,
                'current_active_emergencies': 0
            }
        
        return Response(data)
