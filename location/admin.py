from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'timestamp', 'is_emergency')
    list_filter = ('is_emergency', 'timestamp')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'timestamp'
