from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15)
    address = models.TextField()

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)