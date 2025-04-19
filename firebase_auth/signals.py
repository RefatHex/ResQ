from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile when a new user is created via Firebase authentication
    """
    if created and instance.firebase_uid and hasattr(User, 'profile'):
        try:
            from users.models import Profile
            if not hasattr(instance, 'profile'):
                Profile.objects.create(user=instance)
        except ImportError:
            pass  # Profile model might not exist
