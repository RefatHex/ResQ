import uuid
from django.db import models
from users.models import User

class RouteRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    waypoints = models.JSONField(blank=True, null=True)  
    avoid_hazards = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Route from {self.start_location} to {self.end_location}"

class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(RouteRequest, on_delete=models.CASCADE, related_name='routes')
    polyline = models.TextField()  # Encoded polyline from Google Directions API
    distance = models.FloatField()  # Kilometers
    duration = models.FloatField()  # Minutes
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Route {self.id}"