from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    """
    Create JWT tokens for the user
    """
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['user_id'] = user.user_id
    refresh['email'] = user.email
    refresh['is_root_admin'] = user.is_root_admin
    refresh['is_reseller_admin'] = user.is_reseller_admin
    refresh['user_type'] = user.user_type
    
    # Add department admin claims
    from department.models import DepartmentAdmin
    is_department_admin = DepartmentAdmin.objects.filter(user=user).exists()
    refresh['is_department_admin'] = is_department_admin
    
    # If user is a department admin, include the departments they manage
    if is_department_admin:
        managed_departments = DepartmentAdmin.objects.filter(user=user).values_list('department_id', flat=True)
        refresh['managed_departments'] = list(managed_departments)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on user permissions"""
        user = self.request.user
        
        # Root admins can see all users
        if user.is_root_admin:
            return User.objects.all()
        
        # Reseller admins can see users in their departments
        if user.is_reseller_admin:
            from reseller.models import ResellerAdmin, ResellerCustomer
            reseller_admin = ResellerAdmin.objects.filter(user=user).first()
            if reseller_admin:
                # Get all departments under this reseller
                departments = ResellerCustomer.objects.filter(
                    reseller=reseller_admin.reseller
                ).values_list('department', flat=True)
                # Return all users in those departments
                return User.objects.filter(departments__department__in=departments).distinct()
        
        # Regular users can only see themselves
        return User.objects.filter(user_id=user.user_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

class UserProfileAPIView(APIView):
    """
    API endpoint to get or update current user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update current user profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = []  # Allow unauthenticated access
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(email=email, password=password)
            
            if user:
                tokens = get_tokens_for_user(user)
                user_data = UserSerializer(user).data
                
                response_data = {
                    'user': user_data,
                    'tokens': tokens
                }
                
                # If user is a department admin, include detailed department information
                from department.models import DepartmentAdmin
                if user_data.get('is_department_admin'):
                    from department.serializers import DepartmentDetailSerializer
                    
                    # Get departments where user is an admin
                    department_admins = DepartmentAdmin.objects.filter(user=user)
                    departments = [admin.department for admin in department_admins]
                    
                    # Serialize departments with detailed information
                    department_data = DepartmentDetailSerializer(departments, many=True).data
                    response_data['admin_departments'] = department_data
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    """
    API endpoint for user registration
    
    Supports two workflows:
    1. Direct customer registration (default)
    2. Reseller customer registration (when reseller_id is provided)
    """
    permission_classes = []  # Allow unauthenticated access for direct customer registration
    
    def post(self, request):
        # Check if this is a reseller registration
        reseller_id = request.data.get('reseller_id')
        
        if reseller_id:
            # For reseller customers, permission check is required
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required for reseller customer registration"}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            # Verify the reseller exists
            from reseller.models import Reseller, ResellerAdmin, ResellerCustomer
            try:
                reseller = Reseller.objects.get(reseller_id=reseller_id)
            except Reseller.DoesNotExist:
                return Response({"error": "Reseller not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if current user is a root admin or an admin for this reseller
            if not (request.user.is_root_admin or 
                    ResellerAdmin.objects.filter(user=request.user, reseller=reseller).exists()):
                return Response({"error": "You don't have permission to register customers for this reseller"}, 
                              status=status.HTTP_403_FORBIDDEN)
        
        # Register the user
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Set user type based on registration path
            if reseller_id:
                user = serializer.save(user_type='reseller')
            else:
                user = serializer.save(user_type='direct')
            
            tokens = get_tokens_for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
            
            # If this is a reseller registration, create department and link it to reseller
            if reseller_id:
                from reseller.models import Reseller, ResellerCustomer
                from department.models import Department
                
                # Create a department for this customer
                department_name = request.data.get('department_name', f"{user.full_name}'s Department")
                department = Department.objects.create(
                    name=department_name,
                    description=f"Department for {user.full_name}",
                    customer_type='reseller'
                )
                
                # Link department to reseller
                ResellerCustomer.objects.create(
                    reseller=reseller,
                    department=department,
                    is_active=True
                )
                
                # Add department info to response
                from department.serializers import DepartmentSerializer
                response_data['department'] = DepartmentSerializer(department).data
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token_api(request):
    """
    Refresh JWT token
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        user_id = refresh.payload.get('user_id')
        
        if user_id:
            user = get_object_or_404(User, user_id=user_id)
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
    API endpoint to invalidate refresh token
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        refresh.blacklist()
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
