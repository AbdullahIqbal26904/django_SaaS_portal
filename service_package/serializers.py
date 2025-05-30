from rest_framework import serializers
from .models import ServicePackage, Subscription, ServiceAccess, Transaction
from department.serializers import DepartmentSerializer
from user.serializers import UserSerializer

class ServicePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePackage
        fields = ['id', 'name', 'description', 'price', 'billing_cycle', 'features', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    department_details = DepartmentSerializer(source='department', read_only=True)
    service_package_details = ServicePackageSerializer(source='service_package', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'department', 'service_package', 'status', 'start_date', 'end_date', 
                 'created_at', 'updated_at', 'department_details', 'service_package_details']
        read_only_fields = ['id', 'created_at', 'updated_at', 'department_details', 'service_package_details']

class ServiceAccessSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    subscription_details = SubscriptionSerializer(source='subscription', read_only=True)
    service_package_details = ServicePackageSerializer(source='service_package', read_only=True)
    
    class Meta:
        model = ServiceAccess
        fields = ['id', 'user', 'subscription', 'service_package', 'granted_at', 
                 'user_details', 'subscription_details', 'service_package_details']
        read_only_fields = ['id', 'granted_at', 'user_details', 'subscription_details', 'service_package_details']

class TransactionSerializer(serializers.ModelSerializer):
    subscription_details = SubscriptionSerializer(source='subscription', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'subscription', 'amount', 'status', 'payment_date', 
                 'payment_method', 'transaction_id', 'created_at', 'subscription_details']
        read_only_fields = ['id', 'created_at', 'subscription_details']
