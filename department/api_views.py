from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Department, DepartmentAdmin, DepartmentUser
from .serializers import DepartmentSerializer, DepartmentDetailSerializer, DepartmentAdminSerializer, DepartmentUserSerializer
from user.models import User

# Department ViewSet
class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for departments
    """
    queryset = Department.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailSerializer
        return DepartmentSerializer
    
    def perform_create(self, serializer):
        department = serializer.save()
        # Automatically make the creator an admin
        DepartmentAdmin.objects.create(
            user=self.request.user, 
            department=department
        )

# Department Admin views
class DepartmentAdminAPI(APIView):
    """
    API endpoint for managing department administrators
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, department_id):
        """Add a user as department admin"""
        # Only root admins can create department admins
        if not request.user.is_root_admin:
            return Response({"error": "Only root administrators can assign department administrators"}, 
                          status=status.HTTP_403_FORBIDDEN)
                          
        department = get_object_or_404(Department, department_id=department_id)
        email = request.data.get('email')
        full_name = request.data.get('full_name')
        password = request.data.get('password')
        
        if not email or not full_name:
            return Response({"error": "Email and full name are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user with given email already exists
        user = User.objects.filter(email=email).first()
        
        if user:
            # If user exists, check if they're already an admin for this department
            if DepartmentAdmin.objects.filter(user=user, department=department).exists():
                return Response(
                    {"error": "User is already an admin of this department"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Create a new user with the provided information
            if not password:
                return Response({"error": "Password is required for new users"}, 
                              status=status.HTTP_400_BAD_REQUEST)
                              
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                password=password
            )
        
        # Create department admin relationship
        admin = DepartmentAdmin.objects.create(user=user, department=department)
        serializer = DepartmentAdminSerializer(admin)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, department_id):
        """Remove a user from department admins"""
        department = get_object_or_404(Department, department_id=department_id)
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        admin = get_object_or_404(DepartmentAdmin, user__email=email, department=department)
        admin.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

# Department User views
class DepartmentUserAPI(APIView):
    """
    API endpoint for managing department users
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, department_id):
        """Add a user to department"""
        # Check if the requester is a department admin
        department = get_object_or_404(Department, department_id=department_id)
        
        if not (request.user.is_root_admin or 
                DepartmentAdmin.objects.filter(user=request.user, department=department).exists()):
            return Response({"error": "Only department administrators can add users to departments"}, 
                          status=status.HTTP_403_FORBIDDEN)
                          
        email = request.data.get('email')
        full_name = request.data.get('full_name')
        password = request.data.get('password')
        
        if not email or not full_name:
            return Response({"error": "Email and full name are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user with given email already exists
        user = User.objects.filter(email=email).first()
        
        if user:
            # If user exists, check if they're already in this department
            if DepartmentUser.objects.filter(user=user, department=department).exists():
                return Response(
                    {"error": "User is already in this department"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Create a new user with the provided information
            if not password:
                return Response({"error": "Password is required for new users"}, 
                              status=status.HTTP_400_BAD_REQUEST)
                              
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                password=password
            )
        
        # Add user to department
        dept_user = DepartmentUser.objects.create(user=user, department=department)
        serializer = DepartmentUserSerializer(dept_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, department_id, user_id=None):
        """Remove a user from department"""
        department = get_object_or_404(Department, department_id=department_id)
        
        # Check permissions
        if not (request.user.is_root_admin or 
                DepartmentAdmin.objects.filter(user=request.user, department=department).exists()):
            return Response({"error": "Only department administrators can remove users"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # If user_id is in the URL, use it, otherwise look for email in request data
        if user_id:
            user = get_object_or_404(User, user_id=user_id)
        else:
            email = request.data.get('email')
            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            user = get_object_or_404(User, email=email)
        
        dept_user = get_object_or_404(DepartmentUser, user=user, department=department)
        dept_user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
