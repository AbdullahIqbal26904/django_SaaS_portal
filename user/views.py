from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.http import HttpResponse, JsonResponse
from allauth.socialaccount.models import SocialApp, SocialAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
# import JWT libraries
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_tokens_for_user(user):
    """
    Create JWT tokens for the user.
    """
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['user_id'] = user.user_id
    refresh['email'] = user.email
    refresh['is_root_admin'] = user.is_root_admin
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def login_view(request):
    # If user is already logged in with Django auth (which Google Auth uses)
    if request.user.is_authenticated:
        # Set our custom session variables
        request.session['user_id'] = request.user.user_id
        request.session['user_email'] = request.user.email
        return redirect("dashboard")
    
    # Add social account providers to the context
    socialaccount_providers = []
    try:
        # Check if Google is configured
        google_app = SocialApp.objects.get(provider='google')
        socialaccount_providers.append({
            'id': 'google',
            'name': 'Google'
        })
    except SocialApp.DoesNotExist:
        pass

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Use Django's authenticate function
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Log the user in using Django's session-based auth
            login(request, user)
            
            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            
            # Set session variables
            request.session['user_id'] = user.user_id
            request.session['user_email'] = user.email
            
            # Create response
            response = redirect("dashboard")
            
            # Set JWT cookies
            response.set_cookie(
                'access_token',
                tokens['access'],
                max_age=3600,  # 1 hour
                samesite='Lax',
                httponly=True
            )
            response.set_cookie(
                'refresh_token', 
                tokens['refresh'], 
                httponly=True, 
                max_age=86400,  # 1 day
                samesite='Lax'
            )
            
            return response
        else:
            return render(request, "login.html", {
                "error": "Invalid email or password",
                "socialaccount_providers": socialaccount_providers
            })

    return render(request, "login.html", {"socialaccount_providers": socialaccount_providers})
def dashboard(request):
    # Check if user is logged in via Django auth
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Get user object (should already be available in request.user)
    user = request.user
    
    # Set session variables for backwards compatibility
    request.session['user_id'] = user.user_id
    request.session['user_email'] = user.email
    
    # Get department information
    departments = []
    from department.models import Department, DepartmentAdmin, DepartmentUser
    
    # If user is root admin, get all departments
    if user.is_root_admin:
        departments = Department.objects.all()[:5]  # Limit to 5 for dashboard
    else:
        # Get departments where user is an admin or member
        admin_departments = Department.objects.filter(admins__user=user)
        user_departments = Department.objects.filter(users__user=user)
        departments = (admin_departments | user_departments).distinct()[:5]
    
    # Get service packages information
    from service_package.models import ServicePackage, Subscription, ServiceAccess
    
    # Get active subscriptions
    if user.is_root_admin:
        subscriptions = Subscription.objects.filter(status='active')[:5]
    else:
        # Get subscriptions for departments where user is an admin
        admin_department_ids = DepartmentAdmin.objects.filter(user=user).values_list('department_id', flat=True)
        subscriptions = Subscription.objects.filter(department_id__in=admin_department_ids, status='active')[:5]
    
    # Get service access for this user
    services = ServiceAccess.objects.filter(user=user)
    
    # Render the dashboard template with user info
    return render(request, "dashboard.html", {
        "user": user,
        "departments": departments,
        "subscriptions": subscriptions,
        "services": services,
        "is_root_admin": user.is_root_admin
    })

def sign_out(request):
    # Clear the session
    request.session.flush()
    logout(request)

    # Create response object to clear cookies
    response = redirect("login")
    # Clear JWT cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    print('token flushed')
    return response

@csrf_exempt
def refresh_token(request):
    """Endpoint to refresh an expired access token"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    refresh_token = request.COOKIES.get('refresh_token')
    
    if not refresh_token:
        return JsonResponse({'error': 'Refresh token required'}, status=400)
    
    try:
        # Verify the refresh token
        token = RefreshToken(refresh_token)
        
        # Get user from token
        user_id = token.payload.get('user_id')
        user = User.objects.get(user_id=user_id)
        
        # Generate new tokens
        tokens = get_tokens_for_user(user)
        
        # Set cookies in response
        response = JsonResponse({'message': 'Token refreshed successfully'})
        response.set_cookie(
            'access_token', 
            tokens['access'], 
            httponly=True, 
            max_age=3600,
            samesite='Lax'
        )
        response.set_cookie(
            'refresh_token', 
            tokens['refresh'], 
            httponly=True, 
            max_age=86400,
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': 'Invalid refresh token'}, status=401)

# ...existing code...

@csrf_exempt
def test_jwt(request):
    """Test endpoint to verify JWT authentication is working"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user_id': request.user.user_id,
            'email': request.user.email,
            'is_root_admin': request.user.is_root_admin,
            'message': 'JWT authentication is working correctly!'
        })
    else:
        return JsonResponse({
            'authenticated': False,
            'message': 'JWT authentication failed or not present'
        }, status=401)