from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register('packages', api_views.ServicePackageViewSet, basename='service-package')
router.register('subscriptions', api_views.SubscriptionViewSet, basename='subscription')
router.register('transactions', api_views.TransactionViewSet, basename='transaction')

urlpatterns = [
    # API endpoints using ViewSets
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('subscribe/', api_views.SubscribeAPIView.as_view(), name='subscribe_api'),
    path('subscription-users/<int:subscription_id>/', api_views.ServiceAccessAPIView.as_view(), name='subscription_users_api'),
]
