from django.test import TestCase
from django.contrib.auth import get_user_model
from chats.models import ChatRoom, Message

User = get_user_model()

class ChatRoomModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')

    def test_chatroom_creation(self):
        room = ChatRoom.objects.create(user1=self.user1, user2=self.user2)
        self.assertEqual(str(room), f"Chat between {self.user1.username} and {self.user2.username}")

    def test_unique_chatroom(self):
        ChatRoom.objects.create(user1=self.user1, user2=self.user2)
        with self.assertRaises(Exception):
            ChatRoom.objects.create(user1=self.user1, user2=self.user2)

    def test_message_creation(self):
        room = ChatRoom.objects.create(user1=self.user1, user2=self.user2)
        msg = Message.objects.create(chat_room=room, sender=self.user1, content='Hello!')
        self.assertFalse(msg.is_read)
        self.assertEqual(msg.content, 'Hello!')
        self.assertEqual(msg.chat_room, room)
