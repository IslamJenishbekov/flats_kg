from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from . import views


urlpatterns = [
    path('registrate/', views.registrate, name='registrate'),
    path('login/', views.login, name='login')
]