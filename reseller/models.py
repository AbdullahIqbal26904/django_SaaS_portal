from django.db import models
from user.models import User
from department.models import Department
from django.utils import timezone

class Reseller(models.Model):
    """
    Represents a reseller/partner who can manage their own customers (departments)
    and offer services to them.
    """
    reseller_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resellers'
    
    def __str__(self):
        return self.name


class ResellerAdmin(models.Model):
    """
    Links users to resellers as administrators.
    A reseller admin can manage departments under their reseller account.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reseller_admin')
    reseller = models.ForeignKey(Reseller, on_delete=models.CASCADE, related_name='admins')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reseller_admins'
        unique_together = ('user', 'reseller')
    
    def __str__(self):
        return f"{self.user.full_name} - {self.reseller.name} Admin"


class ResellerCustomer(models.Model):
    """
    Links departments to resellers as customers.
    """
    id = models.AutoField(primary_key=True)
    reseller = models.ForeignKey(Reseller, on_delete=models.CASCADE, related_name='customers')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='reseller')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reseller_customers'
        unique_together = ('reseller', 'department')
    
    def __str__(self):
        return f"{self.reseller.name} - {self.department.name}"
