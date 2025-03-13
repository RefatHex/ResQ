# map_services/serializers.py
from rest_framework import serializers
from .models import RouteRequest, Route

class RouteRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = RouteRequest
        fields = [
            'id', 'user', 'start_location', 'end_location', 
            'waypoints', 'avoid_hazards', 'timestamp'
        ]

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'request', 'polyline', 'distance', 'duration', 'timestamp']