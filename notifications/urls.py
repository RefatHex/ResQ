from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('register-token/', views.register_fcm_token, name='register-fcm-token'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
]
