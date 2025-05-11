from django.contrib import admin
from .models import Department, DepartmentAdmin, DepartmentUser

@admin.register(Department)
class DepartmentModelAdmin(admin.ModelAdmin):
    list_display = ('department_id', 'name', 'created_at')
    search_fields = ('name',)
    
@admin.register(DepartmentAdmin)
class DepartmentAdminModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'user')
    search_fields = ('department__name', 'user__email')
    
@admin.register(DepartmentUser)
class DepartmentUserModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'user')
    search_fields = ('department__name', 'user__email')
