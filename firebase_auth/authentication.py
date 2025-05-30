from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
import requests
import json
from django.conf import settings

User = get_user_model()

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for Django REST Framework that authenticates 
    users using Firebase ID tokens without requiring the Admin SDK.
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Firebase '):
            return None
            
        # Extract the token
        id_token = auth_header.split(' ')[1]
        if not id_token:
            return None
            
        try:
            # Verify the token using Firebase Auth REST API
            firebase_api_key = settings.FIREBASE_CONFIG['apiKey']
            verification_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={firebase_api_key}"
            
            response = requests.post(
                verification_url,
                json={"idToken": id_token}
            )
            
            if response.status_code != 200:
                error_data = response.json()
                raise AuthenticationFailed(f"Firebase token verification failed: {error_data.get('error', {}).get('message')}")
            
            user_data = response.json().get('users', [])[0]
            firebase_uid = user_data.get('localId')
            email = user_data.get('email', '')
            
            # Get or create user
            try:
                user = User.objects.get(firebase_uid=firebase_uid)
            except User.DoesNotExist:
                # Check if a user with this email already exists
                try:
                    if email:
                        user = User.objects.get(email=email)
                        # Update the user's Firebase UID
                        user.firebase_uid = firebase_uid
                        user.save()
                    else:
                        raise User.DoesNotExist
                except User.DoesNotExist:
                    # Create a new user
                    username = email or firebase_uid
                    
                    # Ensure username is unique
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}_{counter}"
                        counter += 1
                    
                    # Create user with plain text password (using firebase_uid as password)
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=firebase_uid, # Store firebase_uid as plain text password
                        firebase_uid=firebase_uid
                    )
                    
            return (user, None)
            
        except Exception as e:
            print(f"Firebase auth error: {str(e)}")
            return None
