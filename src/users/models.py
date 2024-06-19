from dotenv import load_dotenv
from django.contrib.auth.models import AbstractUser
from django.db import models
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
class Customer(AbstractUser):
    name = models.CharField(max_length=200)
    mail = models.EmailField(max_length=200)
    age = models.IntergerField(null=True, blank=True)
    profile_pic = CloudinaryField(upload_to='data', null=True, blank=True)
    preferences = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name