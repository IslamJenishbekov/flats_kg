from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # Django будет хешировать пароль
    role = models.CharField(max_length=50)
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    tel_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
