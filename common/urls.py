from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from . import views


urlpatterns = [
    path('about/', views.tell_about, name='about'),
]