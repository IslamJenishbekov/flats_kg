from django.urls import path
from . import views

urlpatterns = [
    path('my_chats/', views.my_chats, name='my_chats'),
    path('start_chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('get_new_messages/<int:room_id>/', views.get_new_messages, name='get_new_messages'),
    path('send_message/<int:room_id>/', views.send_message, name='send_message'),
]
