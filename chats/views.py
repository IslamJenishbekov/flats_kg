# chat/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from django.db.models import Q
import json


@login_required
def get_new_messages(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    last_message_id = request.GET.get('last_message_id', 0)
    new_messages = Message.objects.filter(chat_room=chat_room, id__gt=last_message_id).order_by('timestamp')

    messages_data = [
        {
            'id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%H:%M')
        } for message in new_messages
    ]
    return JsonResponse({'messages': messages_data})


@login_required
def send_message(request, room_id):
    if request.method == 'POST':
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        data = json.loads(request.body)
        message = Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=data['message']
        )
        return JsonResponse({'success': True, 'message_id': message.id})
    return JsonResponse({'success': False}, status=400)


def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    messages = Message.objects.filter(chat_room=chat_room).order_by('timestamp')

    # Отмечаем все сообщения от другого пользователя как прочитанные
    other_user = chat_room.user1 if chat_room.user2 == request.user else chat_room.user2
    Message.objects.filter(chat_room=chat_room, sender=other_user, is_read=False).update(is_read=True)

    return render(request, 'chats/chat_room.html', {
        'chat_room': chat_room,
        'messages': messages,
    })


@login_required
def start_chat(request, user_id):
    User = get_user_model()
    other_user = get_object_or_404(User, id=user_id)

    # Проверяем, есть ли комната для этих пользователей
    chat_room = ChatRoom.objects.filter(user1=request.user, user2=other_user).first()
    if not chat_room:
        chat_room = ChatRoom.objects.filter(user1=other_user, user2=request.user).first()

    if not chat_room:
        # Если комнаты нет, создаем новую
        chat_room = ChatRoom.objects.create(user1=request.user, user2=other_user)

    # Перенаправляем в комнату чата
    return redirect('chat_room', room_id=chat_room.id)


@login_required
def my_chats(request):
    # Получаем все комнаты, где пользователь участвует
    chat_rooms = ChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user))

    # Собираем данные о чатах и уведомлениях
    chat_list = []
    for room in chat_rooms:
        other_user = room.user1 if room.user2 == request.user else room.user2
        unread_count = Message.objects.filter(
            chat_room=room,
            sender=other_user,  # Сообщения от другого пользователя
            is_read=False
        ).count()
        chat_list.append({
            'room': room,
            'other_user': other_user,
            'unread_count': unread_count
        })

    return render(request, 'chats/my_chats.html', {'chat_list': chat_list})
