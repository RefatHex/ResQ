from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('global/', views.GlobalAnalyticsView.as_view(), name='global_analytics'),
    path('regional/', views.RegionalAnalyticsView.as_view(), name='regional_analytics'),
    path('user/', views.UserAnalyticsView.as_view(), name='user_analytics'),
]
