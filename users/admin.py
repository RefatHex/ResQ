from django.contrib import admin
from .models import User, DeviceToken

# Register your models here.
admin.site.register(User)
admin.site.register(DeviceToken)
