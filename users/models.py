from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField

class UserProfile(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    username = models.CharField(max_length=200, unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    preferences = models.JSONField(null=True, blank=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class UserEmbeddings(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="embedding")
    embeddings = ArrayField(models.FloatField(), size=512)

    def __str__(self):
        return f"Embeddings for user {self.user.username}"