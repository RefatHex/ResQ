
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}  # Hide password

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user