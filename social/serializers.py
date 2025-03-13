# social/serializers.py
from rest_framework import serializers
from .models import SocialPost

class SocialPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPost
        fields = [
            'id', 'platform', 'content', 'photo', 'video', 
            'status', 'timestamp'
        ]
        extra_kwargs = {
            'photo': {'required': False},
            'video': {'required': False}
        }