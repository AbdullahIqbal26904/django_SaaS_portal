from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Reseller, ResellerAdmin, ResellerCustomer
from .serializers import ResellerSerializer, ResellerDetailSerializer, ResellerAdminSerializer, ResellerCustomerSerializer
from user.models import User
from department.models import Department
from service_package.models import Subscription, ServicePackage
import datetime

# Custom permissions
class IsRootAdminOrResellerAdmin(BasePermission):
    """
    Permission to check if user is root admin or a reseller admin
    """
    def has_permission(self, request, view):
        # Root admins have full permission
        if request.user.is_root_admin:
            return True
            
        # For list and retrieve operations, allow reseller admins
        if request.method == 'GET':
            return ResellerAdmin.objects.filter(user=request.user).exists()
            
        # For create operations, only root admins can create resellers
        if view.action == 'create':
            return request.user.is_root_admin
            
        # For detail actions (update, delete), check in has_object_permission
        return True
    
    def has_object_permission(self, request, view, obj):
        # Root admins have full permission
        if request.user.is_root_admin:
            return True
            
        # For GET operations, allow related reseller admins
        if request.method == 'GET':
            return ResellerAdmin.objects.filter(user=request.user, reseller=obj).exists()
        
        # For other operations, only root admins are allowed
        return request.user.is_root_admin

# Reseller ViewSet
class ResellerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for resellers/partners
    """
    queryset = Reseller.objects.all()
    permission_classes = [IsAuthenticated, IsRootAdminOrResellerAdmin]
    
    def get_queryset(self):
        """
        Filter resellers based on user permissions:
        - Root admins see all resellers
        - Reseller admins see only their resellers
        """
        user = self.request.user
        
        # Root admins can see all resellers
        if user.is_root_admin:
            return Reseller.objects.all()
            
        # Get resellers where user is an admin
        return Reseller.objects.filter(admins__user=user).distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResellerDetailSerializer
        return ResellerSerializer

# Reseller Admin API
class ResellerAdminAPI(APIView):
    """
    API endpoint for managing reseller administrators
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, reseller_id):
        """Add a user as reseller admin"""
        # Only root admins can create reseller admins
        if not request.user.is_root_admin:
            return Response({"error": "Only root administrators can assign reseller administrators"}, 
                          status=status.HTTP_403_FORBIDDEN)
                          
        reseller = get_object_or_404(Reseller, reseller_id=reseller_id)
        email = request.data.get('email')
        full_name = request.data.get('full_name')
        password = request.data.get('password')
        
        if not email or not full_name:
            return Response({"error": "Email and full name are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user with given email already exists
        user = User.objects.filter(email=email).first()
        
        if user:
            # If user exists, check if they're already an admin for this reseller
            if ResellerAdmin.objects.filter(user=user, reseller=reseller).exists():
                return Response(
                    {"error": "User is already an admin of this reseller"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Update existing user to be a reseller admin if they aren't already
            if not user.is_reseller_admin:
                user.is_reseller_admin = True
                user.user_type = 'reseller'
                user.save()
        else:
            # Create a new user with the provided information
            if not password:
                return Response({"error": "Password is required for new users"}, 
                              status=status.HTTP_400_BAD_REQUEST)
                              
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                password=password,
                is_reseller_admin=True,
                user_type='reseller'
            )
            user.is_reseller_admin = True
            user.user_type = 'reseller'
            user.save()
        
        # Create reseller admin relationship
        admin = ResellerAdmin.objects.create(user=user, reseller=reseller)
        serializer = ResellerAdminSerializer(admin)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, reseller_id):
        """Remove a user from reseller admins"""
        # Only root admins can delete reseller admins
        if not request.user.is_root_admin:
            return Response({"error": "Only root administrators can remove reseller administrators"}, 
                          status=status.HTTP_403_FORBIDDEN)
                          
        reseller = get_object_or_404(Reseller, reseller_id=reseller_id)
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        admin = get_object_or_404(ResellerAdmin, user__email=email, reseller=reseller)
        admin.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

# Reseller Customer API
class ResellerCustomerAPI(APIView):
    """
    API endpoint for managing customers under a reseller
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, reseller_id):
        """Get all customers for a reseller"""
        reseller = get_object_or_404(Reseller, reseller_id=reseller_id)
        
        # Check if user has permission to view this reseller's customers
        if not (request.user.is_root_admin or 
                ResellerAdmin.objects.filter(user=request.user, reseller=reseller).exists()):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        customers = ResellerCustomer.objects.filter(reseller=reseller)
        serializer = ResellerCustomerSerializer(customers, many=True)
        return Response(serializer.data)
    
    def post(self, request, reseller_id):
        """Add a customer to a reseller"""
        reseller = get_object_or_404(Reseller, reseller_id=reseller_id)
        
        # Check if user has permission to add customers to this reseller
        if not (request.user.is_root_admin or 
                ResellerAdmin.objects.filter(user=request.user, reseller=reseller).exists()):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        # Create a new department for the customer
        name = request.data.get('name')
        description = request.data.get('description')
        
        if not name:
            return Response({"error": "Customer name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the department with customer_type set to 'reseller'
        department = Department.objects.create(
            name=name,
            description=description,
            customer_type='reseller'
        )
        
        # Create the reseller-customer relationship
        customer = ResellerCustomer.objects.create(
            reseller=reseller,
            department=department,
            is_active=True
        )
        
        serializer = ResellerCustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, reseller_id, customer_id):
        """Remove a customer from a reseller"""
        reseller = get_object_or_404(Reseller, reseller_id=reseller_id)
        
        # Check if user has permission to remove customers from this reseller
        if not (request.user.is_root_admin or 
                ResellerAdmin.objects.filter(user=request.user, reseller=reseller).exists()):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        customer = get_object_or_404(ResellerCustomer, id=customer_id, reseller=reseller)
        customer.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

# Reseller Subscription API
class ResellerSubscriptionAPI(APIView):
    """
    API endpoint for managing subscriptions for reseller customers
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, reseller_id):
        """Create a subscription for a reseller customer"""
        reseller = get_object_or_404(Reseller, reseller_id=reseller_id)
        
        # Check if user has permission to create subscriptions for this reseller's customers
        if not (request.user.is_root_admin or 
                ResellerAdmin.objects.filter(user=request.user, reseller=reseller).exists()):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        department_id = request.data.get('department')
        package_id = request.data.get('service_package')
        
        # Validate inputs
        if not department_id or not package_id:
            return Response(
                {"error": "Department ID and Service Package ID are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if department exists and belongs to this reseller
        try:
            customer = ResellerCustomer.objects.get(
                department__department_id=department_id, 
                reseller=reseller
            )
            department = customer.department
        except ResellerCustomer.DoesNotExist:
            return Response({"error": "Customer not found under this reseller"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if service package exists
        try:
            service_package = ServicePackage.objects.get(id=package_id)
        except ServicePackage.DoesNotExist:
            return Response({"error": "Service package not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate subscription dates based on billing cycle
        start_date = datetime.date.today()
        if service_package.billing_cycle == 'monthly':
            end_date = start_date + datetime.timedelta(days=30)
        elif service_package.billing_cycle == 'quarterly':
            end_date = start_date + datetime.timedelta(days=90)
        elif service_package.billing_cycle == 'yearly':
            end_date = start_date + datetime.timedelta(days=365)
        else:
            end_date = start_date + datetime.timedelta(days=30)  # Default to monthly
        
        # Create the subscription with reseller information
        subscription = Subscription.objects.create(
            department=department,
            service_package=service_package,
            start_date=start_date,
            end_date=end_date,
            status='active',
            subscription_source='reseller',
            reseller=reseller
        )
        
        from service_package.serializers import SubscriptionSerializer
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
