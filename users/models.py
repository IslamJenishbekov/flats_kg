from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # Хешируем пароль
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=50)
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    tel_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)  # Обязательное поле
    is_staff = models.BooleanField(default=False)  # Обязательное поле

    objects = UserManager()  # Подключаем кастомный менеджер

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []  # Дополнительные обязательные поля (можно добавить `role`)

    def __str__(self):
        return self.username
