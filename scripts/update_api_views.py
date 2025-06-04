#!/usr/bin/env python

"""
Script to fix the SubscribeAPIView and ServiceAccessAPIView to support reseller functionality.
This script modifies the service_package/api_views.py file directly.

Run with:
python update_api_views.py
"""

import re
import os

def update_service_package_api_views():
    file_path = 'service_package/api_views.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update SubscribeAPIView's post method
    subscribe_pattern = re.compile(r'# Check if user has permission to create subscription for this department\s+if not user.is_root_admin and not department.admins\.filter\(user=user\)\.exists\(\):\s+return Response\(\{"error": "Permission denied"\}, status=status\.HTTP_403_FORBIDDEN\)')
    
    new_permission_check = """# Check if user has permission to create subscription for this department
        has_permission = False
        reseller = None
        subscription_source = 'direct'
        
        # Root admin can manage all subscriptions
        if user.is_root_admin:
            has_permission = True
        
        # Department admin can manage their department's subscriptions
        elif department.admins.filter(user=user).exists():
            has_permission = True
        
        # Reseller admin can manage their customer subscriptions
        elif user.is_reseller_admin:
            from reseller.models import ResellerAdmin, ResellerCustomer
            reseller_admin = ResellerAdmin.objects.filter(user=user).first()
            if reseller_admin:
                reseller = reseller_admin.reseller
                # Check if department is a customer of this reseller
                if ResellerCustomer.objects.filter(
                    reseller=reseller,
                    department=department
                ).exists():
                    has_permission = True
                    subscription_source = 'reseller'
        
        if not has_permission:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)"""
    
    content = re.sub(subscribe_pattern, new_permission_check, content)
    
    # Update subscription creation to include reseller fields
    subscription_pattern = re.compile(r'# Create the subscription\s+subscription = Subscription\.objects\.create\(\s+department=department,\s+service_package=service_package,\s+start_date=start_date,\s+end_date=end_date,\s+status=\'active\'\s+\)')
    
    new_subscription_creation = """# Create the subscription
        subscription = Subscription.objects.create(
            department=department,
            service_package=service_package,
            start_date=start_date,
            end_date=end_date,
            status='active',
            subscription_source=subscription_source,
            reseller=reseller
        )"""
    
    content = re.sub(subscription_pattern, new_subscription_creation, content)
    
    # Update ServiceAccessAPIView permission checks to include resellers
    service_access_get_pattern = re.compile(r'# Check permissions\s+user = request\.user\s+if not user\.is_root_admin and not subscription\.department\.admins\.filter\(user=user\)\.exists\(\):\s+return Response\(\{"error": "Permission denied"\}, status=status\.HTTP_403_FORBIDDEN\)')
    
    new_service_access_get = """# Check permissions
        user = request.user
        has_permission = False
        
        # Root admin has full access
        if user.is_root_admin:
            has_permission = True
        
        # Department admin has access to their department
        elif subscription.department.admins.filter(user=user).exists():
            has_permission = True
        
        # Reseller admin has access to their customer subscriptions
        elif user.is_reseller_admin and subscription.subscription_source == 'reseller':
            from reseller.models import ResellerAdmin
            has_permission = ResellerAdmin.objects.filter(
                user=user, 
                reseller=subscription.reseller
            ).exists()
        
        if not has_permission:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)"""
    
    content = re.sub(service_access_get_pattern, new_service_access_get, content)
    
    # Update ServiceAccessAPIView post method permission checks
    service_access_post_pattern = re.compile(r'# Check permissions\s+user = request\.user\s+if not user\.is_root_admin and not subscription\.department\.admins\.filter\(user=user\)\.exists\(\):\s+return Response\(\{"error": "Permission denied"\}, status=status\.HTTP_403_FORBIDDEN\)')
    
    content = re.sub(service_access_post_pattern, new_service_access_get, content)
    
    # Write the modified content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {file_path} with reseller support")

if __name__ == "__main__":
    # Make sure we're in the right directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    update_service_package_api_views()
