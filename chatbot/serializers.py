# chatbot/serializers.py
from rest_framework import serializers
from .models import ChatSession

class ChatSessionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'message', 'response', 'timestamp']