from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Notification
from .serializers import NotificationSerializer, FCMTokenSerializer
from users.models import DeviceToken

class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class NotificationListView(APIView):
    """List all notifications for the current user"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class NotificationDetailView(APIView):
    """Get, update, or delete a specific notification"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            # Only allow updating is_read status
            if 'is_read' in request.data:
                notification.is_read = request.data['is_read']
                notification.save()
                serializer = NotificationSerializer(notification)
                return Response(serializer.data)
            return Response({'error': 'Only is_read field can be updated'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_fcm_token(request):
    """Register or update a user's FCM token for push notifications"""
    serializer = FCMTokenSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        fcm_token = serializer.validated_data['fcm_token']
        device_type = serializer.validated_data.get('device_type', 'ANDROID')
        
        # Save in both user model for backward compatibility
        user.fcm_token = fcm_token
        user.save()
        
        # Create or update DeviceToken entry
        device_token, created = DeviceToken.objects.update_or_create(
            user=user,
            token=fcm_token,
            defaults={
                'device_type': device_type,
                'is_active': True
            }
        )
        
        return Response({'status': 'FCM token registered'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    Notification.objects.filter(recipient=request.user).update(is_read=True)
    return Response({'status': 'All notifications marked as read'}, status=status.HTTP_200_OK)
