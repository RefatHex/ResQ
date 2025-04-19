from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, EmergencyLocationsListView

router = DefaultRouter()
router.register(r'', LocationViewSet, basename='location')

urlpatterns = [
    path('', include(router.urls)),
    path('emergency-locations/', EmergencyLocationsListView.as_view(), name='emergency-locations'),
]
