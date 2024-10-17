# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=6, blank=True, null=True)
