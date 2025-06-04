from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ServicePackage, Subscription, ServiceAccess, Transaction
from .serializers import ServicePackageSerializer, SubscriptionSerializer, ServiceAccessSerializer, TransactionSerializer
from department.models import Department
from user.models import User
from datetime import datetime, timedelta

# Service Package ViewSet
class ServicePackageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for service packages
    """
    queryset = ServicePackage.objects.all()
    serializer_class = ServicePackageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only active packages by default"""
        queryset = ServicePackage.objects.all()
        active_only = self.request.query_params.get('active_only', 'true').lower() == 'true'
        
        if active_only:
            queryset = queryset.filter(is_active=True)
            
        return queryset

# Subscription ViewSet
class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for subscriptions
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter subscriptions based on user permissions"""
        user = self.request.user
        
        # Root admins can see all subscriptions
        if user.is_root_admin:
            return Subscription.objects.all()
        
        # Reseller admins can see subscriptions for their customers
        if user.is_reseller_admin:
            from reseller.models import ResellerAdmin, ResellerCustomer
            reseller_admin = ResellerAdmin.objects.filter(user=user).first()
            if reseller_admin:
                # Get all departments under this reseller
                departments = ResellerCustomer.objects.filter(
                    reseller=reseller_admin.reseller
                ).values_list('department', flat=True)
                # Return subscriptions for those departments
                return Subscription.objects.filter(
                    department__in=departments
                ).order_by('-created_at')
            
        # Department admins can see their department's subscriptions
        admin_departments = Department.objects.filter(admins__user=user)
        return Subscription.objects.filter(department__in=admin_departments)
    
    def create(self, request):
        """Create a new subscription"""
        user = request.user
        data = request.data
        
        # Get department and service package
        department_id = data.get('department')
        package_id = data.get('service_package')
        
        # Validate inputs
        if not department_id or not package_id:
            return Response(
                {"error": "Department ID and Service Package ID are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if department exists
        try:
            department = Department.objects.get(department_id=department_id)
        except Department.DoesNotExist:
            return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Check if service package exists
        try:
            service_package = ServicePackage.objects.get(id=package_id)
        except ServicePackage.DoesNotExist:
            return Response({"error": "Service package not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Check if user has permission to create subscription for this department
        if not user.is_root_admin and not department.admins.filter(user=user).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate subscription dates based on billing cycle
        start_date = datetime.today().date()
        if service_package.billing_cycle == 'monthly':
            end_date = start_date + timedelta(days=30)
        elif service_package.billing_cycle == 'quarterly':
            end_date = start_date + timedelta(days=90)
        elif service_package.billing_cycle == 'yearly':
            end_date = start_date + timedelta(days=365)
        else:
            end_date = start_date + timedelta(days=30)  # Default to monthly
        
        # Create the subscription
        subscription = Subscription.objects.create(
            department=department,
            service_package=service_package,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Subscribe API View
class SubscribeAPIView(APIView):
    """
    API endpoint for creating subscriptions
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new subscription"""
        user = request.user
        data = request.data
        
        # Get department and service package
        department_id = data.get('department')
        package_id = data.get('service_package')
        
        # Validate inputs
        if not department_id or not package_id:
            return Response(
                {"error": "Department ID and Service Package ID are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if department exists
        try:
            department = Department.objects.get(department_id=department_id)
        except Department.DoesNotExist:
            return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Check if service package exists
        try:
            service_package = ServicePackage.objects.get(id=package_id)
        except ServicePackage.DoesNotExist:
            return Response({"error": "Service package not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Check if user has permission to create subscription for this department
        if not user.is_root_admin and not department.admins.filter(user=user).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate subscription dates based on billing cycle
        start_date = datetime.today().date()
        if service_package.billing_cycle == 'monthly':
            end_date = start_date + timedelta(days=30)
        elif service_package.billing_cycle == 'quarterly':
            end_date = start_date + timedelta(days=90)
        elif service_package.billing_cycle == 'yearly':
            end_date = start_date + timedelta(days=365)
        else:
            end_date = start_date + timedelta(days=30)  # Default to monthly
        
        # Create the subscription
        subscription = Subscription.objects.create(
            department=department,
            service_package=service_package,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        # Return the subscription details
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Service Access API View
class ServiceAccessAPIView(APIView):
    """
    API endpoint for managing user access to subscribed services
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, subscription_id):
        """Get users with access to a subscription"""
        # Get the subscription
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Check permissions
        user = request.user
        if not user.is_root_admin and not subscription.department.admins.filter(user=user).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
        # Get all service access records for this subscription
        access_records = ServiceAccess.objects.filter(subscription=subscription)
        serializer = ServiceAccessSerializer(access_records, many=True)
        return Response(serializer.data)
    
    def post(self, request, subscription_id):
        """Grant a user access to a subscription"""
        # Get the subscription
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Check permissions
        user = request.user
        if not user.is_root_admin and not subscription.department.admins.filter(user=user).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        # Get the user to grant access to
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if access already exists
        if ServiceAccess.objects.filter(
            user=target_user, 
            subscription=subscription,
            service_package=subscription.service_package
        ).exists():
            return Response({"error": "User already has access to this service"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the service access
        service_access = ServiceAccess.objects.create(
            user=target_user,
            subscription=subscription,
            service_package=subscription.service_package
        )
        
        serializer = ServiceAccessSerializer(service_access)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, subscription_id):
        """Remove a user's access to a subscription"""
        # Get the subscription
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Check permissions
        user = request.user
        if not user.is_root_admin and not subscription.department.admins.filter(user=user).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        # Get the user to remove access from
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete the service access
        deleted, _ = ServiceAccess.objects.filter(
            user__user_id=user_id,
            subscription=subscription
        ).delete()
        
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "User does not have access to this service"}, status=status.HTTP_404_NOT_FOUND)

# Transaction ViewSet
class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for transactions
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter transactions based on user permissions"""
        user = self.request.user
        
        # Root admins can see all transactions
        if user.is_root_admin:
            return Transaction.objects.all()
            
        # Department admins can see their department's transactions
        admin_departments = Department.objects.filter(admins__user=user)
        return Transaction.objects.filter(subscription__department__in=admin_departments)
