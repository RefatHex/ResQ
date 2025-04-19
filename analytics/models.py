from django.db import models
from django.utils import timezone
from django.conf import settings

class SystemMetric(models.Model):
    """Track system-wide metrics"""
    date = models.DateField(default=timezone.now)
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    emergency_reports = models.IntegerField(default=0)
    resolved_emergencies = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"System Metrics for {self.date}"

class RegionalMetric(models.Model):
    """Track metrics by region/area"""
    REGION_CHOICES = [
        ('NORTH', 'North'),
        ('SOUTH', 'South'),
        ('EAST', 'East'),
        ('WEST', 'West'),
        ('CENTRAL', 'Central'),
        # Add more regions as needed
    ]
    
    date = models.DateField(default=timezone.now)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    emergency_count = models.IntegerField(default=0)
    response_time_avg = models.FloatField(default=0)  # Average response time in minutes
    
    class Meta:
        ordering = ['-date', 'region']
        unique_together = ['date', 'region']
        
    def __str__(self):
        return f"{self.region} Metrics for {self.date}"

class UserActivity(models.Model):
    """Track individual user activity"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    logins = models.IntegerField(default=0)
    reports_submitted = models.IntegerField(default=0)
    notifications_received = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
        
    def __str__(self):
        return f"Activity for {self.user.username} on {self.date}"

class EmergencyTypeMetric(models.Model):
    """Track metrics by emergency type"""
    date = models.DateField(default=timezone.now)
    emergency_type = models.CharField(max_length=50)  # corresponds to EmergencyTag.emergency_type
    count = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0)  # in minutes
    resolution_rate = models.FloatField(default=0)  # percentage
    
    class Meta:
        ordering = ['-date', 'emergency_type']
        unique_together = ['date', 'emergency_type']
        
    def __str__(self):
        return f"{self.emergency_type} Metrics for {self.date}"
