import base64
import json
from io import BytesIO

from PIL import Image
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from moderation.models import UserBlocking
from users.forms import CustomUserCreationForm
from users.models import *
from listings.models import Listing


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
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


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
