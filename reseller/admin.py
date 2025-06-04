from django.contrib import admin
from .models import Reseller, ResellerAdmin, ResellerCustomer

@admin.register(Reseller)
class ResellerModelAdmin(admin.ModelAdmin):
    list_display = ('reseller_id', 'name', 'is_active', 'commission_rate', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(ResellerAdmin)
class ResellerAdminModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'reseller', 'user', 'assigned_at')
    search_fields = ('reseller__name', 'user__email')

@admin.register(ResellerCustomer)
class ResellerCustomerModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'reseller', 'department', 'is_active', 'created_at')
    search_fields = ('reseller__name', 'department__name')
    list_filter = ('is_active',)
