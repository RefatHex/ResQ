from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginView, UserListView, UserLoginView, UserRegistrationView, UserDetailView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('', include(router.urls)),
]
