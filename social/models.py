import uuid
from django.db import models

from location.models import Location
from users.models import User

class SocialPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    PLATFORM_CHOICES = [
        ('FACEBOOK', 'Facebook'),
        ('TELEGRAM', 'Telegram'),
        ('DISCORD', 'Discord'),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content = models.TextField()
    photo = models.ImageField(upload_to='social_photos/', blank=True, null=True)  # Optional photo
    video = models.FileField(upload_to='social_videos/', blank=True, null=True)  # Optional video
    status = models.CharField(max_length=20, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.timestamp}"
    
    
class Hazard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hazard_type = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['hazard_type', 'timestamp'])]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.hazard_type} - {self.location}"