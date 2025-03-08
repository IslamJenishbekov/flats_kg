from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from users.forms import CustomUserCreationForm
from users.models import *
import base64
from io import BytesIO
from PIL import Image


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
    return render(request, 'users/profile.html')


class RegisterUser(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


def show_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user == user:
        return redirect('users:profile')
    return render(request, 'users/another_profile.html', {'user': user})
