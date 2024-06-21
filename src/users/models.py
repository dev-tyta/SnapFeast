from dotenv import load_dotenv
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload
import cloudinary
import os

load_dotenv()

cloudinary_key = os.getenv('CLOUDINARY_KEY')
cloudinary_secret = os.getenv('CLOUDINARY_SECRET')

cloudinary.config(
    cloud_name="snapfeast",
    api_key=cloudinary_key,
    api_secret=cloudinary_secret
)

# Create your models here.
class UserProfile(AbstractUser):
    first_name = models.CharField(max_length=200, blank=False)
    last_name = models.CharField(max_length=200, blank=False)
    mail = models.EmailField(max_length=200, unique=True)
    age = models.IntegerField(null=True, blank=True)
    preferences = models.JSONField(null=True, blank=True)
    embeddings = ArrayField(models.FloatField(), null=True, blank=True)

    def __str__(self):
        return self.name
    
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
