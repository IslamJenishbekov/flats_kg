from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('all/', views.show_all_listings, name='all_listings'),
                  path('create_listing/', views.create_listing, name='create_listing'),
                  path('my_listings3', views.show_my_listings, name='my_listings'),
                  path('details_<int:listing_id>/', views.show_listing_detail, name='listing_detail'),
                  path('main_chat_assistant/', views.main_chat_view, name='main_chat_assistant'),
                  path('listing_chat_assistant', views.listing_chat_view, name='listing_chat_assistant'),
                  path('users/', include('users.urls')),
                  path('my_favorites/', views.show_my_favorites, name='my_favorites'),
                  path('edit_<int:listing_id>/', views.edit_listing, name='edit_listing'),
                  path('delete_<int:listing_id>/', views.delete_listing, name='delete_listing')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
