from django.urls import path
from .views import profile_view, RegisterUser

app_name = "users"

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
]
