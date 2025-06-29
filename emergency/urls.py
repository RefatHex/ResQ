from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EmergencyTagViewSet,
    EmergencyReportViewSet,
    NearbyEmergenciesView,
    EmergencyStatsByTagView
)

router = DefaultRouter()
# Ensure trailing slashes for viewsets
router.register(r'reports', EmergencyReportViewSet, basename='emergencyreport')
router.register(r'tags', EmergencyTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add trailing slashes to other URLs
    path('nearby/', NearbyEmergenciesView.as_view(), name='nearby-emergencies'),
    path('stats/tags/', EmergencyStatsByTagView.as_view(), name='emergency-tag-stats'),
]
