# emergency/serializers.py
from rest_framework import serializers
from .models import EmergencyReport, EmergencyTag, Hazard

class EmergencyTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyTag
        fields = ['id', 'name', 'description']

class EmergencyReportSerializer(serializers.ModelSerializer):
    reporter = serializers.PrimaryKeyRelatedField(read_only=True)  # Auto-set to current user
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    tags = EmergencyTagSerializer(many=True, required=False)

    class Meta:
        model = EmergencyReport
        fields = [
            'id', 'reporter', 'reporter_type', 'description', 
            'location', 'is_emergency', 'status', 'timestamp', 'tags'
        ]

class HazardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    class Meta:
        model = Hazard
        fields = ['id', 'hazard_type', 'user', 'location', 'description', 'timestamp']