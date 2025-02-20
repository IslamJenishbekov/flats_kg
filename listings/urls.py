from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from . import views


urlpatterns = [
    path('all/', views.show_all_listings, name='all_listings')
]