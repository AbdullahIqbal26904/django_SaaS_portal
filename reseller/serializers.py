from rest_framework import serializers
from .models import Reseller, ResellerAdmin, ResellerCustomer
from user.serializers import UserSerializer
from department.serializers import DepartmentSerializer

class ResellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reseller
        fields = ['reseller_id', 'name', 'description', 'is_active', 'commission_rate', 'created_at', 'updated_at']
        read_only_fields = ['reseller_id', 'created_at', 'updated_at']

class ResellerDetailSerializer(serializers.ModelSerializer):
    admins = serializers.SerializerMethodField()
    customers = serializers.SerializerMethodField()
    
    class Meta:
        model = Reseller
        fields = ['reseller_id', 'name', 'description', 'is_active', 'commission_rate', 
                  'created_at', 'updated_at', 'admins', 'customers']
        read_only_fields = ['reseller_id', 'created_at', 'updated_at']
    
    def get_admins(self, obj):
        reseller_admins = ResellerAdmin.objects.filter(reseller=obj).select_related('user')
        return UserSerializer([admin.user for admin in reseller_admins], many=True).data
    
    def get_customers(self, obj):
        reseller_customers = ResellerCustomer.objects.filter(reseller=obj).select_related('department')
        return DepartmentSerializer([customer.department for customer in reseller_customers], many=True).data

class ResellerAdminSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    reseller_details = ResellerSerializer(source='reseller', read_only=True)
    
    class Meta:
        model = ResellerAdmin
        fields = ['id', 'user', 'reseller', 'assigned_at', 'user_details', 'reseller_details']
        read_only_fields = ['id', 'assigned_at', 'user_details', 'reseller_details']

class ResellerCustomerSerializer(serializers.ModelSerializer):
    department_details = DepartmentSerializer(source='department', read_only=True)
    reseller_details = ResellerSerializer(source='reseller', read_only=True)
    
    class Meta:
        model = ResellerCustomer
        fields = ['id', 'reseller', 'department', 'is_active', 'created_at',
                 'department_details', 'reseller_details']
        read_only_fields = ['id', 'created_at', 'department_details', 'reseller_details']
