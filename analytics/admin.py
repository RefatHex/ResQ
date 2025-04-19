from django.contrib import admin
from .models import SystemMetric, RegionalMetric, UserActivity, EmergencyTypeMetric

@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'active_users', 'new_users', 'emergency_reports', 'resolved_emergencies')
    list_filter = ('date',)

@admin.register(RegionalMetric)
class RegionalMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'region', 'emergency_count', 'response_time_avg')
    list_filter = ('date', 'region')

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'logins', 'reports_submitted', 'notifications_received')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email')

@admin.register(EmergencyTypeMetric)
class EmergencyTypeMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'emergency_type', 'count', 'avg_response_time', 'resolution_rate')
    list_filter = ('date', 'emergency_type')
