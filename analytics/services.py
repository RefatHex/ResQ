from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Min, Max
from collections import defaultdict

from .models import SystemMetric, RegionalMetric, UserActivity, EmergencyTypeMetric
from emergency.models import EmergencyReport
from users.models import User
from notifications.models import Notification

def collect_daily_metrics():
    """
    Collect and save daily system metrics
    Should be run by a scheduler (e.g., Celery) once per day
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Check if metrics for yesterday already exist
    if SystemMetric.objects.filter(date=yesterday).exists():
        return False  # Already collected
    
    # Count active users (those who logged in)
    active_users = User.objects.filter(
        last_login__date=yesterday
    ).count()
    
    # Count new users
    new_users = User.objects.filter(
        date_joined__date=yesterday
    ).count()
    
    # Count emergency reports
    emergency_reports = EmergencyReport.objects.filter(
        timestamp__date=yesterday
    ).count()
    
    # Count resolved emergencies
    resolved_emergencies = EmergencyReport.objects.filter(
        timestamp__date=yesterday,
        status='RESOLVED'
    ).count()
    
    # Save system metrics
    SystemMetric.objects.create(
        date=yesterday,
        active_users=active_users,
        new_users=new_users,
        emergency_reports=emergency_reports,
        resolved_emergencies=resolved_emergencies
    )
    
    # Collect emergency type metrics
    collect_emergency_type_metrics(yesterday)
    
    # Collect regional metrics
    collect_regional_metrics(yesterday)
    
    # Collect user activity
    collect_user_activity(yesterday)
    
    return True

def collect_emergency_type_metrics(date):
    """Collect metrics for each emergency type on the given date"""
    from emergency.models import EmergencyTag
    
    # Get all emergency types
    emergency_types = EmergencyTag.objects.values_list('emergency_type', flat=True).distinct()
    
    for e_type in emergency_types:
        # Get reports for this type
        reports = EmergencyReport.objects.filter(
            timestamp__date=date,
            tags__emergency_type=e_type
        )
        
        # Skip if no reports
        if not reports.exists():
            continue
        
        # Count total reports for this type
        total_count = reports.count()
        
        # Count resolved reports
        resolved = reports.filter(status='RESOLVED').count()
        
        # Calculate resolution rate
        resolution_rate = (resolved / total_count) * 100 if total_count > 0 else 0
        
        # Calculate average response time (placeholder - need to implement based on your data model)
        # This would require tracking when a report status changes to RESPONDING
        avg_response_time = 0
        
        # Save metrics
        EmergencyTypeMetric.objects.create(
            date=date,
            emergency_type=e_type,
            count=total_count,
            avg_response_time=avg_response_time,
            resolution_rate=resolution_rate
        )

def collect_regional_metrics(date):
    """Collect metrics for each region on the given date"""
    # This is a placeholder - you need to implement region determination
    # based on your data model (e.g., geocoding based on lat/lng)
    
    # Example implementation
    reports_by_region = defaultdict(list)
    
    # Assign reports to regions (simplified example)
    for report in EmergencyReport.objects.filter(timestamp__date=date):
        # Simplified region determination based on coordinates
        # In a real app, you would use geocoding or predefined regions
        if report.latitude and report.longitude:
            if report.latitude > 0 and report.longitude > 0:
                region = 'NORTH'
            elif report.latitude > 0 and report.longitude < 0:
                region = 'WEST'
            elif report.latitude < 0 and report.longitude > 0:
                region = 'EAST'
            elif report.latitude < 0 and report.longitude < 0:
                region = 'SOUTH'
            else:
                region = 'CENTRAL'
                
            reports_by_region[region].append(report)
    
    # Calculate metrics for each region
    for region, reports in reports_by_region.items():
        # Count reports
        count = len(reports)
        
        # Calculate average response time (placeholder)
        response_time_avg = 0
        
        # Save regional metrics
        RegionalMetric.objects.create(
            date=date,
            region=region,
            emergency_count=count,
            response_time_avg=response_time_avg
        )

def collect_user_activity(date):
    """Collect activity metrics for each user on the given date"""
    # Get all users who were active on the given date
    active_users = User.objects.filter(
        last_login__date=date
    )
    
    for user in active_users:
        # Count logins (simplified - assuming 1 login per day)
        logins = 1
        
        # Count reports submitted
        reports_submitted = EmergencyReport.objects.filter(
            reporter=user,
            timestamp__date=date
        ).count()
        
        # Count notifications received
        notifications_received = Notification.objects.filter(
            recipient=user,
            timestamp__date=date
        ).count()
        
        # Save user activity
        UserActivity.objects.create(
            user=user,
            date=date,
            logins=logins,
            reports_submitted=reports_submitted,
            notifications_received=notifications_received
        )
