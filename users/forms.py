from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Импортируем нашу модель


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Указываем свою модель
        fields = ("username", "tg_link", "tel_number")
