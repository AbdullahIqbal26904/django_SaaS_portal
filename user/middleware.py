import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .models import User
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        Process request to authenticate via JWT token
        """
        # Skip authentication for login & static URLs
        if request.path == '/login/' or request.path.startswith('/admin/') or \
           request.path.startswith('/accounts/') or request.path.startswith('/static/'):
            return None

        # Django auth takes precedence
        if request.user.is_authenticated:
            return None

        # Check for token in cookies
        access_token = request.COOKIES.get('access_token')
        
        if not access_token:
            logger.debug(f"No access token found for path: {request.path}")
            # Fall back to session authentication if no token
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(user_id=user_id)
                    request.user = user
                    logger.debug(f"User authenticated via session: {user.email}")
                except User.DoesNotExist:
                    pass
            return None
        
        try:
            # Decode token
            logger.debug(f"Decoding JWT token for path: {request.path}")
            payload = jwt.decode(
                access_token, 
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
            )
            # Get user from token payload
            user_id = payload.get('user_id')
            logger.debug(f"JWT payload user_id: {user_id}")
            
            if user_id:
                try:
                    # Get user and set in request
                    user = User.objects.get(user_id=user_id)
                    request.user = user  # Set this as the Django user
                    logger.debug(f"User authenticated via JWT: {user.email}")
                    
                    # Also set session variables for compatibility
                    request.session['user_id'] = user.user_id
                    request.session['user_email'] = user.email
                    
                except User.DoesNotExist:
                    logger.warning(f"User ID from JWT not found in database: {user_id}")
                
        except jwt.ExpiredSignatureError:
            logger.debug("JWT token expired")
            # Token expired - could add refresh token logic here
            # Redirect to refresh token endpoint
            if request.path != '/refresh_token/':
                # Clear the expired token
                response = redirect('login')
                response.delete_cookie('access_token')
                return response
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            # Invalid token
            pass
            
        return None