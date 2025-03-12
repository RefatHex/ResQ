from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = [
        ('CITIZEN', 'Citizen'),
        ('FIRE_STATION', 'Fire Station'),
        ('POLICE', 'Police'),
        ('RED_CRESCENT', 'Red Crescent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username