from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class UserProfile(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    preferences = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class UserEmbeddings(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="embedding")
    embeddings = ArrayField(models.FloatField(), null=True, blank=True)

    def __str__(self):
        return f"Embeddings for user {self.user.first_name}"