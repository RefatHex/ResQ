from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class PlainTextPasswordBackend(ModelBackend):
    """
    Authentication backend that allows users to log in with plain text passwords
    without hashing the passwords.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Try to authenticate with username
        try:
            user = User.objects.get(username=username)
            if user.password == password:  # Direct comparison without hashing
                return user
        except User.DoesNotExist:
            # Try with email instead
            try:
                user = User.objects.get(email=username)
                if user.password == password:  # Direct comparison without hashing
                    return user
            except User.DoesNotExist:
                return None
        
        return None
