import base64
import json
from io import BytesIO

from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

from moderation.models import UserBlocking
from users.forms import CustomUserCreationForm
from users.models import *
from listings.models import Listing

from django.contrib.auth.models import User


@login_required
def profile_view(request):
    if request.method == 'POST' and 'avatar' in request.FILES:
        avatar_file = request.FILES['avatar']
        img = Image.open(avatar_file)
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        request.user.avatar_base64 = img_base64
        request.user.save()
        return redirect('users:profile')  # Предполагается, что у вас есть name='profile' в urls.py
    if request.user.is_superuser:
        return redirect('custom_admin:admin_profile')
    return render(request, 'users/profile.html')


class RegisterUser(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Save the user and any additional fields (e.g., tg_link, tel_number)
        user = form.save()
        # Save additional fields to a profile model if needed
        # Example: user.profile.tg_link = form.cleaned_data['tg_link']
        # user.profile.tel_number = form.cleaned_data['tel_number']
        # user.profile.save()
        return super().form_valid(form)


def show_user_profile(request, user_id):
    if request.method == "POST" and request.user.role == "moderator":
        data = json.loads(request.body)
        reason = data.get('reason_for_blocking')

        user = get_object_or_404(User, id=user_id)

        blocking = UserBlocking(blocking_cause=reason, user=user)
        blocking.save()

        user.is_blocked = True
        user.save(update_fields=['is_blocked'])

        messages.success(request, "Клиент успешно заблокирован!")
        return redirect("users:another_profile", user_id=user_id)
    user = get_object_or_404(User, id=user_id)

    if request.user.role == "support" and request.method == "POST":
        user.is_blocked = False
        user.save(update_fields=['is_blocked'])
        return redirect('users:another_profile', user_id=user_id)

    elif request.user.role == "support" and user.is_blocked is True:
        blocking = UserBlocking.objects.filter(user=user).order_by('-created_at').first()
        return render(request, 'users/another_profile.html', {'user': user, 'blocking': blocking})
    blocked_listings = Listing.objects.filter(
        user=user,
        is_blocked=True
    )

    if request.user.role == "support" and len(blocked_listings) > 0:
        return render(request, 'users/another_profile.html', context={'user': user, 'has_blocked_listings': True})

    if request.user == user:
        return redirect('users:profile')
    return render(request, 'users/another_profile.html', {'user': user})


@login_required
@require_POST
def change_password(request):
    try:
        # Парсим JSON-данные из тела запроса
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password1 = data.get('new_password1')
        new_password2 = data.get('new_password2')

        # Проверка наличия всех полей
        if not all([old_password, new_password1, new_password2]):
            return JsonResponse({'error': 'Все поля обязательны для заполнения'}, status=400)

        # Проверка совпадения новых паролей
        if new_password1 != new_password2:
            return JsonResponse({'error': 'Новые пароли не совпадают'}, status=400)

        # Проверка длины нового пароля
        if len(new_password1) < 8:
            return JsonResponse({'error': 'Новый пароль должен содержать минимум 8 символов'}, status=400)

        # Проверка, что новый пароль отличается от старого
        if old_password == new_password1:
            return JsonResponse({'error': 'Новый пароль не должен совпадать со старым'}, status=400)

        # Проверка сложности пароля (хотя бы одна заглавная буква и одна цифра)
        if not any(c.isupper() for c in new_password1):
            return JsonResponse({'error': 'Пароль должен содержать хотя бы одну заглавную букву'}, status=400)
        if not any(c.isdigit() for c in new_password1):
            return JsonResponse({'error': 'Пароль должен содержать хотя бы одну цифру'}, status=400)

        # Аутентификация пользователя со старым паролем
        user = authenticate(username=request.user.username, password=old_password)
        if user is None:
            return JsonResponse({'error': 'Неверный старый пароль'}, status=400)

        # Установка нового пароля
        request.user.set_password(new_password1)
        request.user.save()

        return JsonResponse({'success': 'Пароль успешно изменен'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Произошла ошибка: {str(e)}'}, status=500)


@login_required
def change_password_view(request):
    return render(request, 'users/change_password.html')
