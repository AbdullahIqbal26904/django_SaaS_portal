from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ResellerViewSet, ResellerAdminAPI, ResellerCustomerAPI, ResellerSubscriptionAPI

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register('resellers', ResellerViewSet, basename='reseller')

urlpatterns = [
    # API endpoints using ViewSets
    path('', include(router.urls)),
    
    # Custom API endpoints for reseller management
    path('resellers/<int:reseller_id>/admins/', ResellerAdminAPI.as_view(), name='reseller_admin_api'),
    path('resellers/<int:reseller_id>/customers/', ResellerCustomerAPI.as_view(), name='reseller_customer_api'),
    path('resellers/<int:reseller_id>/customers/<int:customer_id>/', ResellerCustomerAPI.as_view(), name='reseller_customer_detail_api'),
    path('resellers/<int:reseller_id>/subscriptions/', ResellerSubscriptionAPI.as_view(), name='reseller_subscription_api'),
]
