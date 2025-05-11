from django.contrib import admin
from .models import ServicePackage, Subscription, ServiceAccess, Transaction

@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'billing_cycle')
    search_fields = ('name',)
    
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'service_package', 'status', 'start_date', 'end_date')
    search_fields = ('department__name', 'service_package__name')
    list_filter = ('status', 'service_package')
    
@admin.register(ServiceAccess)
class ServiceAccessAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscription', 'granted_at')
    search_fields = ('user__email', 'subscription__service_package__name')
    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscription', 'amount', 'status', 'payment_date')
    search_fields = ('subscription__department__name', 'subscription__service_package__name')
    list_filter = ('status',)
