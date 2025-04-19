from django.contrib import admin
from .models import EmergencyReport, EmergencyTag

# Register your models here.
admin.site.register(EmergencyReport)
admin.site.register(EmergencyTag)
