from allauth.socialaccount.signals import social_account_updated, social_account_added
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.db import transaction
from django.utils import timezone
from .models import User
import logging

logger = logging.getLogger(__name__)

@receiver(social_account_added)
@receiver(social_account_updated)
def social_account_handler(sender, request, sociallogin, **kwargs):
    """
    Signal handler for when a social account is added or updated.
    This creates or updates our custom User model and sets session variables.
    """
    try:
        with transaction.atomic():
            # Get the data from the social account
            social_account = sociallogin.account
            email = social_account.extra_data.get('email')
            
            if not email:
                logger.error("No email found in social account data")
                return
                
            # Try to find existing user by email
            try:
                user = User.objects.get(email=email)
                logger.info(f"Found existing user with email: {email}")
                
                # Update oauth provider information
                user.oauth_provider = social_account.provider
                user.oauth_provider_id = social_account.uid
                user.save()
                
            except User.DoesNotExist:
                # Create a new user
                full_name = social_account.extra_data.get('name', '')
                user = User(
                    email=email,
                    full_name=full_name,
                    password_hash='', # No password for social auth users
                    oauth_provider=social_account.provider,
                    oauth_provider_id=social_account.uid,
                    created_at=timezone.now()
                )
                user.save()
                logger.info(f"Created new user with email: {email}")
            
            # Set session variables for the custom auth system
            if request and hasattr(request, 'session'):
                request.session['user_id'] = user.user_id
                request.session['user_email'] = user.email
                logger.info(f"Session variables set for user: {email}")
                
    except Exception as e:
        logger.error(f"Error in social_account_handler: {str(e)}")
