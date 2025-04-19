from django.urls import path
from .views import social_post

urlpatterns = [
    path('post/', social_post, name='social_post'),
]
