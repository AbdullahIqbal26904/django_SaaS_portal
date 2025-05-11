from django.db import models
from user.models import User

class Department(models.Model):
    """
    Department model to organize users in the SaaS platform.
    """
    department_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
    
    def __str__(self):
        return self.name


class DepartmentAdmin(models.Model):
    """
    Links users to departments as administrators.
    A department admin can manage users within their department.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='admins')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'department_admins'
        unique_together = ('user', 'department')
    
    def __str__(self):
        return f"{self.user.full_name} - {self.department.name} Admin"


class DepartmentUser(models.Model):
    """
    Links regular users to departments.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='users')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'department_users'
        unique_together = ('user', 'department')
    
    def __str__(self):
        return f"{self.user.full_name} - {self.department.name}"
