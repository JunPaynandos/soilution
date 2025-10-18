from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth.models import User 
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger('auth')

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_email_taken(self, email):
        User = get_user_model()
        # return User.objects.filter(email=email).exists()
        exists = User.objects.filter(email=email).exists()
        if exists:
            # logger.warning(f"Social login attempt with already registered email: {email}")
            logger.info(f"User with email '{email}' logged in successfully via google login.")
        return exists

    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user

        if not user.id:
            # New social user
            user.is_active = False
            logger.info(f"New social user attempted login: {user.email} — marked inactive until approval.")
            # Let the pipeline continue to save the user to DB
        else:
            # Existing user
            if not user.is_active:
                raise ImmediateHttpResponse(redirect('pending_approval'))
            
         # Handle existing email linked to a user
        if self.is_email_taken(user.email):
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)

        print("🔐 User is inactive, redirecting to pending_approval")

    def authentication_success_url(self, request):
        # Only reached if user is active
        logger.info(f"User {request.user.email} successfully authenticated via social login.")
        return reverse('workspace')

    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
            # Suppress login success messages from django-allauth
            if "signed in" in message_template.lower():
                return  # Don't show the default success message
            super().add_message(request, level, message_template, message_context, extra_tags)

class CustomAccountAdapter(DefaultAccountAdapter):
    def respond_user_inactive(self, request, user):
        return redirect('pending_approval')
