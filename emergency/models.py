import uuid
from django.db import models
from users.models import User

class EmergencyReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    REPORTER_TYPE_CHOICES = [
        ('SPECTATOR', 'Spectator'),
        ('VICTIM', 'Victim'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), 
        ('RESPONDING', 'Emergency Services Responding'),
        ('ON_SCENE', 'Emergency Services On Scene'),
        ('RESOLVED', 'Resolved'),
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reporter_type = models.CharField(max_length=20, choices=REPORTER_TYPE_CHOICES)
    description = models.TextField() 
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_emergency = models.BooleanField(default=False)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)  
    tags = models.ManyToManyField('EmergencyTag', related_name='reports', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['reporter', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.reporter.username} - {self.timestamp}"


class EmergencyTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    EMERGENCY_TYPE_CHOICES = [
        ('FIRE', 'Fire Emergency'),
        ('NATURAL', 'Natural Disaster'),
        ('TRAFFIC', 'Traffic Accident'),
        ('OTHER', 'Other Emergency'),
    ]
    emergency_type = models.CharField(max_length=20, choices=EMERGENCY_TYPE_CHOICES, default='OTHER')
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name