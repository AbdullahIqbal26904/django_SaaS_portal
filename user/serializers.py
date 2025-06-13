from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    is_department_admin = serializers.SerializerMethodField()
    managed_departments = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['user_id', 'email', 'full_name', 'is_root_admin', 'is_reseller_admin', 
                 'user_type', 'mfa_enabled', 'created_at', 'is_department_admin', 'managed_departments']
        read_only_fields = ['user_id', 'created_at', 'is_department_admin', 'managed_departments']
    
    def get_is_department_admin(self, obj):
        from department.models import DepartmentAdmin
        return DepartmentAdmin.objects.filter(user=obj).exists()
    
    def get_managed_departments(self, obj):
        from department.models import DepartmentAdmin
        from department.serializers import DepartmentSerializer
        
        # Only return departments info if the user is a department admin
        departments = [admin.department for admin in DepartmentAdmin.objects.filter(user=obj)]
        if departments:
            return DepartmentSerializer(departments, many=True).data
        return []
        
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'is_root_admin', 'is_reseller_admin', 
                 'user_type', 'mfa_enabled']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
