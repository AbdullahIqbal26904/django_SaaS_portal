from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # API endpoints for each app
    path('users/', include('user.api_urls')),
    path('departments/', include('department.api_urls')),
    path('services/', include('service_package.api_urls')),
    path('resellers/', include('reseller.api_urls')),
    
    # JWT token refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
