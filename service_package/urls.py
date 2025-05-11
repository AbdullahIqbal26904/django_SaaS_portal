from django.urls import path
from . import views

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('create/', views.create_package, name='create_package'),
    path('<int:package_id>/', views.package_detail, name='package_detail'),
    path('<int:package_id>/edit/', views.edit_package, name='edit_package'),
    path('<int:package_id>/subscribe/', views.subscribe_to_package, name='subscribe_to_package'),
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('subscriptions/<int:subscription_id>/', views.subscription_detail, name='subscription_detail'),
    path('subscriptions/<int:subscription_id>/grant-access/', views.grant_service_access, name='grant_service_access'),
    path('subscriptions/<int:subscription_id>/revoke-access/<int:user_id>/', views.revoke_service_access, name='revoke_service_access'),
]
