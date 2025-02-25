from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from users.forms import CustomUserCreationForm


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


class RegisterUser(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_invalid(self, form):
        print(form.errors)  # Вывод ошибок в консоль
        return super().form_invalid(form)
