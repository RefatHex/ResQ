from django.urls import path, include
from rest_framework.routers import DefaultRouter

# We'll add the URL patterns once you build the map_services app views
# For now, we'll just provide an empty router to prevent import errors

router = DefaultRouter()
# Add viewsets here when they're created

urlpatterns = [
    path('', include(router.urls)),
]
