from django.urls import path
from . import views

urlpatterns = [
    path('my_chats/', views.my_chats, name='my_chats'),
    path('start_chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
]
