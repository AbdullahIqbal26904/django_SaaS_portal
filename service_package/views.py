from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ServicePackage, Subscription, ServiceAccess, Transaction
from department.models import Department
from user.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
from datetime import datetime, timedelta

# Service Package Management Views
@login_required
def package_list(request):
    """
    Display all available service packages
    """
    packages = ServicePackage.objects.filter(is_active=True)
    return render(request, 'service_package/package_list.html', {
        'packages': packages,
        'is_root_admin': request.user.is_root_admin
    })

@login_required
def package_detail(request, package_id):
    """
    Display details of a specific service package
    """
    package = get_object_or_404(ServicePackage, id=package_id)
    return render(request, 'service_package/package_detail.html', {
        'package': package,
        'is_root_admin': request.user.is_root_admin
    })

@login_required
def create_package(request):
    """
    Create a new service package (root admin only)
    """
    if not request.user.is_root_admin:
        return redirect('package_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        billing_cycle = request.POST.get('billing_cycle')
        features = request.POST.get('features', '{}')
        
        if name and price and billing_cycle:
            try:
                # Parse features from JSON string
                features_dict = json.loads(features)
                
                package = ServicePackage.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    billing_cycle=billing_cycle,
                    features=features_dict,
                    is_active=True
                )
                return redirect('package_detail', package_id=package.id)
            except json.JSONDecodeError:
                # Handle invalid JSON
                pass
    
    return render(request, 'service_package/create_package.html')

@login_required
def edit_package(request, package_id):
    """
    Edit service package details (root admin only)
    """
    if not request.user.is_root_admin:
        return redirect('package_list')
    
    package = get_object_or_404(ServicePackage, id=package_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        billing_cycle = request.POST.get('billing_cycle')
        features = request.POST.get('features', '{}')
        is_active = request.POST.get('is_active') == 'on'
        
        if name and price and billing_cycle:
            try:
                # Parse features from JSON string
                features_dict = json.loads(features)
                
                package.name = name
                package.description = description
                package.price = price
                package.billing_cycle = billing_cycle
                package.features = features_dict
                package.is_active = is_active
                package.save()
                
                return redirect('package_detail', package_id=package.id)
            except json.JSONDecodeError:
                # Handle invalid JSON
                pass
    
    return render(request, 'service_package/edit_package.html', {'package': package})

# Subscription Management Views
@login_required
def subscription_list(request):
    """
    Display subscriptions based on user role:
    - Root admins see all subscriptions
    - Department admins see only their department's subscriptions
    """
    user = request.user
    
    if user.is_root_admin:
        subscriptions = Subscription.objects.all()
    else:
        # Get departments where user is an admin
        admin_departments = Department.objects.filter(admins__user=user)
        subscriptions = Subscription.objects.filter(department__in=admin_departments)
    
    return render(request, 'service_package/subscription_list.html', {
        'subscriptions': subscriptions,
        'is_root_admin': user.is_root_admin
    })

@login_required
def subscribe_to_package(request, package_id):
    """
    Subscribe a department to a service package
    """
    package = get_object_or_404(ServicePackage, id=package_id)
    
    if request.method == 'POST':
        department_id = request.POST.get('department_id')
        
        if department_id:
            department = get_object_or_404(Department, department_id=department_id)
            
            # Calculate subscription dates based on billing cycle
            start_date = datetime.now().date()
            if package.billing_cycle == 'monthly':
                end_date = start_date + timedelta(days=30)
            elif package.billing_cycle == 'quarterly':
                end_date = start_date + timedelta(days=90)
            elif package.billing_cycle == 'yearly':
                end_date = start_date + timedelta(days=365)
            
            # Create subscription
            subscription = Subscription.objects.create(
                department=department,
                service_package=package,
                start_date=start_date,
                end_date=end_date,
                status='active'
            )
            
            # Create a transaction record
            Transaction.objects.create(
                subscription=subscription,
                amount=package.price,
                payment_date=datetime.now(),
                payment_method='credit_card',  # Simplified for demo
                transaction_id=f'TX-{datetime.now().timestamp()}',  # Simple unique ID
                status='completed'
            )
            
            return redirect('subscription_detail', subscription_id=subscription.id)
    
    # For GET request, show subscription form
    departments = []
    user = request.user
    
    if user.is_root_admin:
        departments = Department.objects.all()
    else:
        # Get departments where user is an admin
        departments = Department.objects.filter(admins__user=user)
    
    return render(request, 'service_package/subscribe_form.html', {
        'package': package,
        'departments': departments
    })

@login_required
def subscription_detail(request, subscription_id):
    """
    View subscription details
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    user = request.user
    
    # Check permissions
    if not user.is_root_admin:
        is_department_admin = subscription.department.admins.filter(user=user).exists()
        
        if not is_department_admin:
            return redirect('subscription_list')
    
    # Get users with access to this subscription
    user_access = ServiceAccess.objects.filter(subscription=subscription)
    
    return render(request, 'service_package/subscription_detail.html', {
        'subscription': subscription,
        'user_access': user_access,
        'transactions': subscription.transactions.all(),
        'is_root_admin': user.is_root_admin,
        'is_department_admin': subscription.department.admins.filter(user=user).exists()
    })

# API endpoints for service package management
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grant_service_access(request, subscription_id):
    """
    Grant access to a service package for a specific user
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    user = request.user
    
    # Check permissions
    if not user.is_root_admin and not subscription.department.admins.filter(user=user).exists():
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    data = json.loads(request.body)
    user_id = data.get('user_id')
    
    if not user_id:
        return Response({"error": "User ID required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        target_user = User.objects.get(user_id=user_id)
        
        # Check if user belongs to the department
        if not target_user.departments.filter(department=subscription.department).exists():
            return Response({
                "error": "User is not a member of this department"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Grant access
        access, created = ServiceAccess.objects.get_or_create(
            user=target_user,
            service_package=subscription.service_package,
            subscription=subscription
        )
        
        if created:
            return Response({
                "message": f"Access granted to {target_user.full_name}"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": f"{target_user.full_name} already has access"
            }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_service_access(request, subscription_id, user_id):
    """
    Revoke access to a service package for a specific user
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    user = request.user
    
    # Check permissions
    if not user.is_root_admin and not subscription.department.admins.filter(user=user).exists():
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        target_user = User.objects.get(user_id=user_id)
        access = ServiceAccess.objects.filter(
            user=target_user,
            service_package=subscription.service_package,
            subscription=subscription
        ).first()
        
        if access:
            access.delete()
            return Response({"message": "Access revoked"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User does not have access"}, status=status.HTTP_404_NOT_FOUND)
        
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
