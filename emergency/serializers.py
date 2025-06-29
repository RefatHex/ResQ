# emergency/serializers.py
from rest_framework import serializers
from .models import EmergencyReport, EmergencyTag

class EmergencyTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyTag
        fields = ['id', 'name', 'emergency_type', 'description']

class EmergencyReportSerializer(serializers.ModelSerializer):
    reporter = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = EmergencyTagSerializer(many=True, required=False, read_only=True)
    tag_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)
    status_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = EmergencyReport
        fields = [
            'id', 'reporter', 'reporter_type', 'description',
            'latitude', 'longitude', 'is_emergency', 'status', 'status_display', 
            'timestamp', 'tags', 'tag_ids'
        ]
    
    def get_status_display(self, obj):
        """Return the human-readable status"""
        return dict(EmergencyReport.STATUS_CHOICES).get(obj.status, obj.status)
    
    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        report = EmergencyReport.objects.create(**validated_data)
        
        # Add tags if provided
        if tag_ids:
            tags = EmergencyTag.objects.filter(id__in=tag_ids)
            report.tags.set(tags)
        
        return report
    
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tag_ids is not None:
            tags = EmergencyTag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)
        
        return instance