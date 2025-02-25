from django.urls import path
from .views import profile_view, RegisterUser


urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
]