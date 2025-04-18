from django.urls import path
from .views import show_admin_profile

app_name = "custom_admin"

urlpatterns = [
    path('admin_profile/', show_admin_profile, name='admin_profile'),
]
