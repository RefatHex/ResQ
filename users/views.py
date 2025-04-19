from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer
from .permissions import IsSameUserOrAdmin
from location.models import Location
from location.serializers import LocationSerializer

class LoginView(TokenObtainPairView):
    """Custom token view that returns user info along with tokens"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # If login successful, include user data
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get('username'))
            user_data = UserSerializer(user).data
            response.data['user'] = user_data
        return response

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
