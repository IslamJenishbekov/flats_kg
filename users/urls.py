from django.urls import path
from .views import profile_view, RegisterUser
from django.contrib.auth.views import LogoutView

app_name = "users"

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout')
]
