from django.db import models
from user.models import User
from department.models import Department

class ServicePackage(models.Model):
    """
    Represents service packages/plans that can be purchased.
    """
    BILLING_CYCLE_CHOICES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    features = models.JSONField(default=dict)  # Stores package features as JSON
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_packages'
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_cycle}"


class Subscription(models.Model):
    """
    Represents a department's subscription to a service package.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    )
    
    id = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subscriptions')
    service_package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
    
    def __str__(self):
        return f"{self.department.name} - {self.service_package.name} ({self.status})"


class ServiceAccess(models.Model):
    """
    Links individual users with specific service packages they can access.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_access')
    service_package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='user_access')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='user_access')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_access'
        unique_together = ('user', 'service_package', 'subscription')
    
    def __str__(self):
        return f"{self.user.full_name} - {self.service_package.name}"


class Transaction(models.Model):
    """
    Records payment transactions for service package subscriptions.
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.AutoField(primary_key=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
    
    def __str__(self):
        return f"{self.transaction_id} - ${self.amount} ({self.status})"
