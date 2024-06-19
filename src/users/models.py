from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Customer(User):
    name = models.CharField(max_length=200)
    mail = models.EmailField(max_length=200)
    phone = models.CharField(max_length=200)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True, blank=True)


    def __str__(self):
        return self.name