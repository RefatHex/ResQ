# chatbot/serializers.py
from rest_framework import serializers
from .models import ChatSession

class ChatSessionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'user_username', 'message', 'response', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000, required=True)
    
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()

class ChatResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    message = serializers.CharField(read_only=True)
    response = serializers.CharField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)