from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'role', 'location', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_active']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    location = serializers.JSONField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 
                 'phone_number', 'role', 'location']
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
        
    def create(self, validated_data):
        """Create a new user with plain text password."""
        print(f"\n=== RegisterSerializer.create ===")
        print(f"Validated data: {validated_data}")
        
        location_data = validated_data.pop('location', None)
        password = validated_data.pop('password')
        
        print(f"Password from validated_data: {password}")
        
        # Use the custom manager's create_user method which handles plain text passwords
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=password,  # This will be stored as plain text
            **{k: v for k, v in validated_data.items() if k not in ['username', 'email']}
        )
        
        print(f"User password after save: {user.password}")
        
        # Add location if provided
        if location_data:
            user.location = location_data
            user.save()
            
        return user