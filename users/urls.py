from django.urls import path
from .views import profile_view, RegisterUser, show_user_profile, change_password, change_password_view
from django.contrib.auth.views import LogoutView

app_name = "users"

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile_<int:user_id>/', show_user_profile, name='another_profile'),
    path('change_password', change_password, name='change_password'),
    path('change-password-view/', change_password_view, name='change_password_view'),
]
