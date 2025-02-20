import django.contrib.auth
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import User
from django.contrib.auth.hashers import check_password


def registrate(request):
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username')
        tg_link = request.POST.get('tg_link')
        tel_number = request.POST.get('tel_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Проверка на совпадение паролей
        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают.')
            return redirect('registrate')

        # Проверка на обязательные поля
        if not username or not password:
            messages.error(request, 'Имя пользователя и пароль обязательны для заполнения.')
            return redirect('registrate')

        # Проверка на уникальность имени пользователя
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return redirect('registrate')

        # Хэширование пароля перед сохранением в базе данных
        hashed_password = make_password(password)

        # Создание нового пользователя
        User.objects.create(
            username=username,
            tg_link=tg_link,
            tel_number=tel_number,
            password=hashed_password
        )

        # Уведомление об успешной регистрации
        messages.success(request, 'Вы успешно зарегистрированы!')

        # Перенаправление на страницу входа
        return redirect('login')

    # Если метод запроса не POST, отображаем страницу регистрации
    return render(request, 'users/registrate.html')


def login_to(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден.')
            return redirect('login')

        if check_password(password, user.password):  # Проверяем пароль
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Указываем backend
            django.contrib.auth.login(request, user)  # Авторизуем пользователя
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('all_listings')  # Перенаправляем после успешного входа
        else:
            messages.error(request, 'Неверный пароль.')
            return redirect('login')

    return render(request, 'users/login.html')


