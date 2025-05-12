import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        logger.info(f"Connecting to room {self.room_id} for user {self.scope['user']}")

        user = self.scope['user']
        if not user.is_authenticated:
            logger.warning("User not authenticated")
            await self.close()
            return

        # Проверяем доступ к комнате асинхронно
        has_access = await self.check_room_access(user)
        if not has_access:
            logger.warning(f"Access denied to room {self.room_id} for user {user}")
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected for room {self.room_id}")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected for room {self.room_id}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.info(f"Received message: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json['message']
            user = self.scope['user']
            logger.info(f"Processing message from {user}: {message_content}")

            message = await self.save_message(user, message_content)
            logger.info(f"Message saved with ID {message.id}")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'sender': user.username,
                        'content': message_content,
                        'timestamp': message.timestamp.strftime('%H:%M')
                    }
                }
            )
            logger.info(f"Message sent to group {self.room_group_name}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    async def chat_message(self, event):
        logger.info(f"Sending message to client: {event['message']}")
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    @database_sync_to_async
    def check_room_access(self, user):
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            return chat_room and (user == chat_room.user1 or user == chat_room.user2)
        except ChatRoom.DoesNotExist:
            logger.error(f"ChatRoom {self.room_id} does not exist")
            return False

    @database_sync_to_async
    def save_message(self, user, content):
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            message = Message.objects.create(
                chat_room=chat_room,
                sender=user,
                content=content
            )
            logger.info(f"Message created: {message.id}")
            return message
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise
