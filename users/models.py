from dotenv import load_dotenv
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload
import cloudinary
import os


# Create your models here.
class UserProfile(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    age = models.IntegerField(null=True, blank=True)
    preferences = models.JSONField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class UserImage(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="images")
    image= CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return f"Image for user {self.user.first_name}"
    

class UserEmbeddings(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="embedding")
    embeddings = ArrayField(models.FloatField(), null=True, blank=True, size=2048)

    def __str__(self):
        return f"Embeddings for user {self.user.first_name}"
