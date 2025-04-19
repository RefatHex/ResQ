from django.apps import AppConfig


class FirebaseAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'firebase_auth'

    def ready(self):
        try:
            import firebase_auth.signals
        except ImportError:
            pass
