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
                response_data = {
                    'user': UserSerializer(user).data,
                    'tokens': tokens
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = []  # Allow unauthenticated access
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
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
