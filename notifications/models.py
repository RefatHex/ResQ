import uuid
from django.db import models
from users.models import User
from emergency.models import EmergencyReport

class Notification(models.Model):
    """Model for storing user notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    NOTIFICATION_TYPES = [
        ('EMERGENCY', 'Emergency Alert'),
        ('UPDATE', 'Status Update'),
        ('SYSTEM', 'System Notification'),
        ('OTHER', 'Other')
    ]
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='OTHER')
    is_read = models.BooleanField(default=False)
    sent_to_device = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional reference to related objects
    emergency_report = models.ForeignKey(
        EmergencyReport, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notifications'
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['recipient', 'timestamp']),
            models.Index(fields=['is_read']),
        ]
        
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"