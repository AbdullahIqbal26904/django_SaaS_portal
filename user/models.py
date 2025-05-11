from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_root_admin', True)
        return self.create_user(email, full_name, password, **extra_fields)

class User(AbstractUser):
    # Keep the default fields from AbstractUser (id, password, is_staff, is_superuser, etc.)
    # Add and customize fields
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    is_root_admin = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)
    oauth_provider = models.CharField(max_length=50, null=True, blank=True)
    oauth_provider_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Override username field to use email instead
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
