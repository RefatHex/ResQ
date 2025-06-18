from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from .models import ChatSession
from .serializers import ChatSessionSerializer, ChatMessageSerializer, ChatResponseSerializer
from .services import ChatbotService
from users.models import User

class ChatViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    """
    ViewSet for managing chat sessions and conversations
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-timestamp')
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send a message to the chatbot and get AI response"""
        serializer = ChatMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            message = serializer.validated_data['message']
            
            # Initialize chatbot service
            chatbot_service = ChatbotService()
            
            # Generate AI response
            ai_response = chatbot_service.generate_response(request.user, message)
            
            # Save chat session
            chat_session = chatbot_service.save_chat_session(
                user=request.user,
                message=message,
                response=ai_response
            )
            
            # Return response
            response_serializer = ChatResponseSerializer({
                'id': chat_session.id,
                'message': message,
                'response': ai_response,
                'timestamp': chat_session.timestamp
            })
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def quick_responses(self, request):
        """Get predefined quick responses for emergency scenarios"""
        chatbot_service = ChatbotService()
        quick_responses = chatbot_service.get_emergency_quick_responses()
        
        return Response(quick_responses, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def session_history(self, request):
        """Get chat session history for the current user"""
        limit = request.query_params.get('limit', 20)
        
        try:
            limit = int(limit)
        except ValueError:
            limit = 20
            
        sessions = self.get_queryset()[:limit]
        serializer = self.get_serializer(sessions, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def clear_history(self, request):
        """Clear all chat history for the current user"""
        deleted_count = ChatSession.objects.filter(user=request.user).delete()[0]
        
        return Response(
            {'message': f'Cleared {deleted_count} chat sessions'},
            status=status.HTTP_200_OK
        )

class ChatBotAPIView(APIView):
    """
    Simple API view for chat interactions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Send message and get response"""
        message = request.data.get('message', '').strip()
        
        if not message:
            return Response(
                {'error': 'Message cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize chatbot service
        chatbot_service = ChatbotService()
        
        try:
            # Generate AI response
            ai_response = chatbot_service.generate_response(request.user, message)
            
            # Save chat session
            chat_session = chatbot_service.save_chat_session(
                user=request.user,
                message=message,
                response=ai_response
            )
            
            return Response({
                'id': str(chat_session.id),
                'message': message,
                'response': ai_response,
                'timestamp': chat_session.timestamp.isoformat(),
                'user_role': request.user.role
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to process message', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_stats(request):
    """Get chat statistics for the current user"""
    user = request.user
    total_sessions = ChatSession.objects.filter(user=user).count()
    
    # Get recent activity (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_sessions = ChatSession.objects.filter(
        user=user,
        timestamp__gte=week_ago
    ).count()
    
    return Response({
        'total_sessions': total_sessions,
        'recent_sessions': recent_sessions,
        'user_role': user.role
    }, status=status.HTTP_200_OK)
