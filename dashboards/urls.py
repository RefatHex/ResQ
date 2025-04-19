from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('citizen/', views.CitizenDashboardView.as_view(), name='citizen_dashboard'),
    path('emergency-service/', views.EmergencyServiceDashboardView.as_view(), name='emergency_service_dashboard'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]
