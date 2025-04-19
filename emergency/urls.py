from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EmergencyTagViewSet,
    EmergencyReportViewSet,
    NearbyEmergenciesView,
    EmergencyStatsByTagView
)

router = DefaultRouter()
router.register(r'tags', EmergencyTagViewSet)
router.register(r'reports', EmergencyReportViewSet, basename='emergencyreport')

urlpatterns = [
    path('', include(router.urls)),
    path('nearby/', NearbyEmergenciesView.as_view(), name='nearby-emergencies'),
    path('stats/tags/', EmergencyStatsByTagView.as_view(), name='emergency-tag-stats'),
]
