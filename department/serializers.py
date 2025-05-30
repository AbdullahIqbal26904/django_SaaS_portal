from rest_framework import serializers
from .models import Department, DepartmentAdmin, DepartmentUser
from user.serializers import UserSerializer

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department_id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['department_id', 'created_at', 'updated_at']

class DepartmentDetailSerializer(serializers.ModelSerializer):
    admins = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['department_id', 'name', 'description', 'created_at', 'updated_at', 'admins', 'users']
        read_only_fields = ['department_id', 'created_at', 'updated_at']
    
    def get_admins(self, obj):
        department_admins = DepartmentAdmin.objects.filter(department=obj).select_related('user')
        return UserSerializer(
            [admin.user for admin in department_admins],
            many=True
        ).data
        
    def get_users(self, obj):
        department_users = DepartmentUser.objects.filter(department=obj).select_related('user')
        return UserSerializer(
            [dept_user.user for dept_user in department_users],
            many=True
        ).data

class DepartmentAdminSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    department_details = DepartmentSerializer(source='department', read_only=True)
    
    class Meta:
        model = DepartmentAdmin
        fields = ['id', 'user', 'department', 'assigned_at', 'user_details', 'department_details']
        read_only_fields = ['id', 'assigned_at', 'user_details', 'department_details']

class DepartmentUserSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    department_details = DepartmentSerializer(source='department', read_only=True)
    
    class Meta:
        model = DepartmentUser
        fields = ['id', 'user', 'department', 'user_details', 'department_details']
        read_only_fields = ['id', 'user_details', 'department_details']
