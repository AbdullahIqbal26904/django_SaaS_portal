from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register('departments', api_views.DepartmentViewSet, basename='department')

urlpatterns = [
    # API endpoints using ViewSets
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('departments/<int:department_id>/admins/', api_views.DepartmentAdminAPI.as_view(), name='department_admin_api'),
    path('departments/<int:department_id>/users/', api_views.DepartmentUserAPI.as_view(), name='department_user_api'),
    path('departments/<int:department_id>/users/<int:user_id>/', api_views.DepartmentUserAPI.as_view(), name='department_user_detail_api'),
]
