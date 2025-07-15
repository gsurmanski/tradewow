from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    #set email as unique field, by default it is not
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)