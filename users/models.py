from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid

class PlainTextUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        Password is stored in plain text without hashing.
        """
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        # Store password as plain text
        if password:
            user.password = password  # Directly set the password without hashing
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given username, email, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('CITIZEN', 'Citizen'),
        ('FIRE_STATION', 'Fire Station'),
        ('POLICE', 'Police'),
        ('RED_CRESCENT', 'Red Crescent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    location = models.JSONField(null=True, blank=True)
    firebase_uid = models.CharField(max_length=128, null=True, blank=True, unique=True)
    fcm_token = models.CharField(max_length=255, null=True, blank=True, help_text='Firebase Cloud Messaging token for push notifications')
    
    objects = PlainTextUserManager()
    
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Make sure the password is not hashed by Django's default behavior
        # by temporarily storing it
        password = self.password
        super(User, self).save(*args, **kwargs)
        # If the save process changed our password (due to hashing), restore original
        if password != self.password:
            self.__class__.objects.filter(pk=self.pk).update(password=password)

class DeviceToken(models.Model):
    """
    Model for storing device tokens for push notifications.
    Each user can have multiple device tokens (one for each device).
    """
    DEVICE_TYPES = (
        ('ANDROID', 'Android'),
        ('IOS', 'iOS'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'token')
        
    def __str__(self):
        return f"{self.user.username}'s {self.device_type} device"