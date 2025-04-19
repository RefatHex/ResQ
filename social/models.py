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
    photo = models.ImageField(upload_to='social_photos/', blank=True, null=True)
    video = models.FileField(upload_to='social_videos/', blank=True, null=True)
    status = models.CharField(max_length=20, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.timestamp}"