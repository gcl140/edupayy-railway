# edupay/pipeline.py
from django.contrib.auth import logout, login
from django.contrib import messages
from django.shortcuts import redirect
from social_core.exceptions import AuthAlreadyAssociated
from social_django.models import UserSocialAuth
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages

def save_user_details(backend, user, response, request=None, *args, **kwargs):
    if backend.name == 'google-oauth2':
        is_new = kwargs.get('is_new', False)

        if is_new or not user.first_name:
            user.first_name = response.get('given_name', user.first_name)

        if is_new or not user.last_name:
            user.last_name = response.get('family_name', user.last_name)

        if is_new:
            user.is_active = True
            user.username = user.email

            user_type = request.session.get('login_user_type', '').lower()
            user.is_parent = (user_type == 'parent')

        user.save()


# def save_user_details(backend, user, response, request=None, *args, **kwargs):
#     if backend.name == 'google-oauth2' and kwargs.get('is_new'):
#         user.is_active = True
#         user.username = user.email  # Set username to email

#         # Use session to determine user type
#         user_type = request.session.get('login_user_type', '').lower()
#         user.is_parent = (user_type == 'parent')
#         user.save()


# def prevent_duplicate_social_auth(strategy, backend, uid, user=None, *args, **kwargs):
#     request = strategy.request
#     existing_social = UserSocialAuth.objects.filter(provider=backend.name, uid=uid).first()

#     if existing_social:
#         if user and existing_social.user != user:
#             # Trying to associate this Google account with another logged-in user
#             messages.error(request, "This Google account is already linked to another user. The previous account has been logged out, you can now login again")
#             logout(request)
#             # return redirect('login')  # or your named login URL
#             return {'user': None}  # Prevent AuthAlreadyAssociated

#         elif not user:
#             # No one logged in – use the existing user associated with this Google account
#             return {'user': existing_social.user}


# edupay/pipeline.py

from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model

def prevent_duplicate_social_auth(strategy, backend, uid, user=None, *args, **kwargs):
    request = strategy.request
    User = get_user_model()

    existing_social = UserSocialAuth.objects.filter(provider=backend.name, uid=uid).first()

    if existing_social:
        if user and existing_social.user != user:
            # A logged-in user is trying to link a Google account that belongs to someone else
            messages.error(request, "This Google account is already linked to another user. You were logged out for security reasons.")
            logout(request)
            return {'user': None}  # Avoid AuthAlreadyAssociated
        elif not user:
            # No one is logged in – use the user already linked to this Google account
            return {'user': existing_social.user}

    # Now handle edge case: email already in DB but not linked via social
    email = kwargs.get('details', {}).get('email')
    if email:
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            # This email is taken by a local user not yet linked to this Google account
            messages.error(request, "A normal account (not linked to Google) with this email already exists. Please login directly using your credentials in the form below.")
            return redirect('login')  # Redirect user to manual login

    # Otherwise allow pipeline to proceed (likely a new user)
    return {}


# from social_core.exceptions import AuthAlreadyAssociated
# from social_django.models import UserSocialAuth
# from django.contrib import messages
# from django.shortcuts import redirect

# def prevent_duplicate_social_auth(backend, uid=None, user=None, *args, **kwargs):
#     if not uid:
#         return

#     strategy = backend.strategy
#     request = strategy.request
#     existing_social = UserSocialAuth.objects.filter(provider=backend.name, uid=uid).first()

#     current_user = kwargs.get('user')

#     if existing_social:
#         if current_user:
#             # If current user is logged in but it's not their social account
#             if existing_social.user != current_user:
#                 messages.error(request, "This Google account is already linked to another user.")
#                 return redirect('login')
#         else:
#             # Automatically associate the existing social account with its user
#             kwargs['user'] = existing_social.user


# def save_user_details(backend, user, response, request=None, *args, **kwargs):
#     if backend.name == 'google-oauth2' and kwargs.get('is_new'):
#         user.is_active = True
#         user.username = user.email  # Use email as username

#         # ✅ Determine user type from URL
#         if request and request.path.startswith("/register/parent"):
#             user.is_parent = True
#         else:
#             user.is_parent = False

#         user.save()
