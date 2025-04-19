"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/locations/', include('location.urls')),
    path('api/emergency/', include('emergency.urls')),
    path('api/social/', include('social.urls')),
    path('api/map/', include('map_services.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/dashboards/', include('dashboards.urls')),
    path('api/analytics/', include('analytics.urls')),
]
# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
