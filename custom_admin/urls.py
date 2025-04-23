from django.urls import path
from .views import show_admin_profile, manage_user_role, manage_filters

app_name = "custom_admin"

urlpatterns = [
    path('admin_profile/', show_admin_profile, name='admin_profile'),
    path('manage-filters/', manage_filters, name='manage_filters'),
    path('set-roles/', manage_user_role, name='set_roles'),
]
