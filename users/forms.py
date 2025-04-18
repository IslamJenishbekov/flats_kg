from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    tg_link = forms.CharField(  # Changed from URLField to CharField
        max_length=200,
        required=True,
        label="Ссылка на Telegram",
        help_text="Введите ссылку на Telegram (например, https://t.me/username)"
    )
    tel_number = forms.CharField(
        max_length=15,
        required=True,
        label="Номер телефона",
        help_text="Введите номер телефона (например, +996123456789)"
    )

    class Meta:
        model = User
        fields = ['username', 'tg_link', 'tel_number', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует.")
        if not re.match(r'^[a-zA-Z0-9_]{3,}$', username):
            raise ValidationError(
                "Имя пользователя должно содержать минимум 3 символа, только буквы, цифры и подчеркивания.")
        return username

    def clean_tg_link(self):
        tg_link = self.cleaned_data.get('tg_link')
        if not re.match(r'^https:\/\/t\.me\/[a-zA-Z0-9_]+$', tg_link):
            raise ValidationError("Введите корректную ссылку на Telegram (например, https://t.me/username).")
        return tg_link

    def clean_tel_number(self):
        tel_number = self.cleaned_data.get('tel_number')
        if not re.match(r'^\+\d{10,15}$', tel_number):
            raise ValidationError("Введите корректный номер телефона (например, +996123456789).")
        return tel_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tg_link = self.cleaned_data['tg_link']
        user.tel_number = self.cleaned_data['tel_number']
        if commit:
            user.save()
        return user
