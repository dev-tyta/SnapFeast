from django.apps import AppConfig
from django.conf import settings

class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        if not settings.DEBUG or settings.TESTING:
            # Import and initialize FacialProcessing
            from utils.facial_processing import FacialProcessing
            FacialProcessing()