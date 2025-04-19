from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from location.models import Location

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = [
        ('CITIZEN', 'Citizen'),
        ('FIRE_STATION', 'Fire Station'),
        ('POLICE', 'Police'),
        ('RED_CRESCENT', 'Red Crescent'),
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True, help_text="Firebase Cloud Messaging token for push notifications")
    firebase_uid = models.CharField(max_length=128, null=True, blank=True, unique=True)

    def __str__(self):
        return self.username

class DeviceToken(models.Model):
    """Store FCM or APNS tokens for push notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255)
    device_type = models.CharField(
        max_length=10, 
        choices=[('ANDROID', 'Android'), ('IOS', 'iOS')]
    )
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'token']
        
    def __str__(self):
        return f"{self.user.username} - {self.device_type} Token"