from django.shortcuts import render


def registrate(request):
    return render(request, 'users/register.html')


def login(request):
    return render(request, 'users/login.html')