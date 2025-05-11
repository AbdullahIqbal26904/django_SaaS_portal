from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Department, DepartmentAdmin, DepartmentUser
from user.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

# Department Dashboard Views
@login_required
def department_list(request):
    """
    Display departments based on user role:
    - Root admins see all departments
    - Department admins see only their departments
    """
    user = request.user
    
    if user.is_root_admin:
        departments = Department.objects.all()
    else:
        # Get departments where user is an admin
        admin_departments = Department.objects.filter(admins__user=user)
        # Get departments where user is a member
        user_departments = Department.objects.filter(users__user=user)
        # Combine both querysets
        departments = (admin_departments | user_departments).distinct()
    
    return render(request, 'department/department_list.html', {
        'departments': departments,
        'is_root_admin': user.is_root_admin
    })

@login_required
def department_detail(request, department_id):
    """
    Display department details and members
    """
    department = get_object_or_404(Department, department_id=department_id)
    
    # Check if user has permission to view this department
    user = request.user
    if not user.is_root_admin:
        is_admin = DepartmentAdmin.objects.filter(user=user, department=department).exists()
        is_member = DepartmentUser.objects.filter(user=user, department=department).exists()
        
        if not (is_admin or is_member):
            return redirect('department_list')
    
    # Get department admins and users
    admins = DepartmentAdmin.objects.filter(department=department)
    members = DepartmentUser.objects.filter(department=department)
    
    return render(request, 'department/department_detail.html', {
        'department': department,
        'admins': admins,
        'members': members,
        'is_root_admin': user.is_root_admin,
        'is_department_admin': DepartmentAdmin.objects.filter(user=user, department=department).exists()
    })

@login_required
def create_department(request):
    """
    Create a new department (root admin only)
    """
    if not request.user.is_root_admin:
        return redirect('department_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            department = Department.objects.create(
                name=name,
                description=description
            )
            return redirect('department_detail', department_id=department.department_id)
    
    return render(request, 'department/create_department.html')

@login_required
def edit_department(request, department_id):
    """
    Edit department details (root admin or department admin only)
    """
    department = get_object_or_404(Department, department_id=department_id)
    user = request.user
    
    # Check permissions
    if not user.is_root_admin and not DepartmentAdmin.objects.filter(user=user, department=department).exists():
        return redirect('department_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            department.name = name
            department.description = description
            department.save()
            return redirect('department_detail', department_id=department.department_id)
    
    return render(request, 'department/edit_department.html', {'department': department})

# API endpoints for department management
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_department_admin(request, department_id):
    """
    Add a user as department admin (root admin only)
    """
    if not request.user.is_root_admin:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    department = get_object_or_404(Department, department_id=department_id)
    data = json.loads(request.body)
    user_email = data.get('user_email')
    
    if not user_email:
        return Response({"error": "User email required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=user_email)
        admin, created = DepartmentAdmin.objects.get_or_create(user=user, department=department)
        
        if created:
            return Response({"message": f"{user.full_name} added as admin"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": f"{user.full_name} is already an admin"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_department_user(request, department_id):
    """
    Add a user to department (root admin or department admin only)
    """
    user = request.user
    department = get_object_or_404(Department, department_id=department_id)
    
    # Check permissions
    if not user.is_root_admin and not DepartmentAdmin.objects.filter(user=user, department=department).exists():
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    data = json.loads(request.body)
    user_email = data.get('user_email')
    
    if not user_email:
        return Response({"error": "User email required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        new_user = User.objects.get(email=user_email)
        dept_user, created = DepartmentUser.objects.get_or_create(user=new_user, department=department)
        
        if created:
            return Response({"message": f"{new_user.full_name} added to department"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": f"{new_user.full_name} is already in the department"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_department_user(request, department_id, user_id):
    """
    Remove a user from department (root admin or department admin only)
    """
    user = request.user
    department = get_object_or_404(Department, department_id=department_id)
    
    # Check permissions
    if not user.is_root_admin and not DepartmentAdmin.objects.filter(user=user, department=department).exists():
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        target_user = User.objects.get(user_id=user_id)
        dept_user = DepartmentUser.objects.filter(user=target_user, department=department).first()
        
        if dept_user:
            dept_user.delete()
            return Response({"message": f"User removed from department"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User is not a member of this department"}, status=status.HTTP_404_NOT_FOUND)
    
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
