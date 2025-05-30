from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register('users', api_views.UserViewSet, basename='user')

urlpatterns = [
    # API endpoints using ViewSets
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/login/', api_views.LoginAPIView.as_view(), name='login_api'),
    path('auth/register/', api_views.RegisterAPIView.as_view(), name='register_api'),
    path('profile/', api_views.UserProfileAPIView.as_view(), name='user_profile_api'),
]
