# notifications/serializers.py
from rest_framework import serializers
from .models import Notification
from users.models import DeviceToken

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'timestamp']
        read_only_fields = ['id', 'title', 'message', 'notification_type', 'timestamp']

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'device_type']

class FCMTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length=255, required=True)
    device_type = serializers.ChoiceField(choices=DeviceToken.DEVICE_TYPES, default='ANDROID')