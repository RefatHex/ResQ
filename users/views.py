from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from .permissions import IsSameUserOrAdmin
from location.models import Location
from location.serializers import LocationSerializer

User = get_user_model()

class LoginView(TokenObtainPairView):
    """Custom token view that returns user info along with tokens"""
    def post(self, request, *args, **kwargs):
        try:
            # Check if credentials are provided
            if not request.data.get('username') or not request.data.get('password'):
                return Response(
                    {"detail": "Username and password are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Try to authenticate and generate tokens
            # Wrap this in try-except to catch authentication errors
            try:
                response = super().post(request, *args, **kwargs)
                
                # If login successful, include user data
                if response.status_code == 200:
                    user = User.objects.get(username=request.data.get('username'))
                    user_data = UserSerializer(user).data
                    response.data['user'] = user_data
                    return response
                return response
            except Exception as auth_error:
                # Handle authentication failure specifically
                return Response(
                    {"detail": "Invalid credentials"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log the error for debugging
            print(f"Login error: {str(e)}")
            return Response(
                {"detail": "Invalid credentials"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class UserViewSet(mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    """
    API endpoint for user operations using mixins for better structure:
    - GET: List all users (admin) or retrieve self
    - POST: Create new user (register)
    - PUT/PATCH: Update user
    - DELETE: Delete user
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_permissions(self):
        """
        - Registration is open to anyone
        - Profile viewing/editing requires authentication
        - Users can only edit their own profiles unless they're admins
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsSameUserOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Register new user with location"""
        print("\n=== UserViewSet.create Request Body ===")
        print(f"Data: {request.data}")
        print("=======================================\n")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create location if provided in the request
            location_data = request.data.get('location')
            if location_data:
                loc_serializer = LocationSerializer(data=location_data)
                if loc_serializer.is_valid():
                    loc_serializer.save(user=user)
            
            # Generate tokens for the user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        """Get locations for a specific user"""
        user = self.get_object()
        # Check permissions - only admins or the user themselves can see their locations
        if not request.user.is_staff and request.user.id != user.id:
            return Response({"detail": "You don't have permission to view these locations"},
                           status=status.HTTP_403_FORBIDDEN)
            
        locations = Location.objects.filter(user=user).order_by('-timestamp')
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

class UserListView(generics.ListAPIView):
    """List users with role-based filtering"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role', None)
        
        if role:
            queryset = queryset.filter(role=role)
        
        # Only admins can see all users, others can only see emergency service users
        if not self.request.user.is_staff:
            # Regular users can only see emergency service providers
            queryset = queryset.filter(role__in=['FIRE_STATION', 'POLICE', 'RED_CRESCENT'])
        
        return queryset

class UserLoginView(APIView):
    """
    View to handle user login with plain text password
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            print(f"\n=== UserLoginView.post ===")
            print(f"Login attempt: username={username}, password={password}")
            
            # Custom authentication logic for plain text passwords
            try:
                # Try with username
                user = User.objects.get(username=username)
                print(f"Found user by username, stored password: '{user.password}'")
                if user.password != password:
                    print(f"Password mismatch: stored='{user.password}', provided='{password}'")
                    user = None
            except User.DoesNotExist:
                try:
                    # Try with email
                    user = User.objects.get(email=username)
                    print(f"Found user by email, stored password: '{user.password}'")
                    if user.password != password:
                        print(f"Password mismatch: stored='{user.password}', provided='{password}'")
                        user = None
                except User.DoesNotExist:
                    print("User not found")
                    user = None
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(APIView):
    """
    View to handle user registration with plain text password
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        print("\n=== UserRegistrationView Request Body ===")
        print(f"Data: {request.data}")
        print("========================================\n")
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Create user with plain text password using the manager's create_user method
            password = serializer.validated_data.get('password')
            print(f"Password before user creation: {password}")
            
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=password,  # This will be stored as plain text by our custom manager
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                phone_number=serializer.validated_data.get('phone_number', ''),
                role=serializer.validated_data.get('role', 'CITIZEN'),
            )
            
            # Set location separately if provided
            location = serializer.validated_data.get('location', None)
            if location:
                user.location = location
                user.save()
                
            print(f"User password after creation: {user.password}")
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user details
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_object(self):
        return self.request.user
