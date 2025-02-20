from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)  # id будет автоматически уникальным и основным ключом
    username = models.CharField(max_length=150, unique=True)  # Имя пользователя
    role = models.CharField(max_length=50)  # Роль пользователя
    tg_link = models.CharField(max_length=255, blank=True, null=True)  # Ссылка на Telegram
    tel_number = models.CharField(max_length=20, blank=True, null=True)  # Номер телефона
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания записи

    def __str__(self):
        return self.username
