from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, ChatBotAPIView, get_chat_stats

router = DefaultRouter()
router.register(r'sessions', ChatViewSet, basename='chat-sessions')


urlpatterns = [
    path('chat/', ChatBotAPIView.as_view(), name='chatbot'),
    path('stats/', get_chat_stats, name='chat-stats'),
    path('', include(router.urls)),
]
