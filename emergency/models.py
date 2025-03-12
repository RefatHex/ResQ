import uuid
from django.db import models
from location.models import Location
from users.models import User

class EmergencyReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    REPORTER_TYPE_CHOICES = [
        ('SPECTATOR', 'Spectator'),
        ('VICTIM', 'Victim'),
    ]
    REPORT_TYPE_CHOICES = [
        ('FIRE', 'Fire'),
        ('ACCIDENT', 'Accident'),
        ('NATURAL_DISASTER', 'Natural Disaster'),
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reporter_type = models.CharField(max_length=20, choices=REPORTER_TYPE_CHOICES)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='emergency_reports')  
    description = models.TextField(blank=True, null=True)
    is_emergency = models.BooleanField(default=False)  # Panic button
    status = models.CharField(max_length=20, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['reporter', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.reporter.username} - {self.report_type}"