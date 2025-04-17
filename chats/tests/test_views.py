from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from chats.models import ChatRoom, Message
import json

User = get_user_model()

class ChatViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='user1', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', password='pass1234')

        self.client.login(username='user1', password='pass1234')

        self.chat_room = ChatRoom.objects.create(user1=self.user1, user2=self.user2)
        self.message = Message.objects.create(
            chat_room=self.chat_room,
            sender=self.user2,
            content='Hello!',
            is_read=False
        )

    def test_get_new_messages(self):
        url = reverse('get_new_messages', args=[self.chat_room.id])
        response = self.client.get(url, {'last_message_id': 0})

        self.assertEqual(response.status_code, 200)
        self.assertIn('messages', response.json())
        self.assertEqual(len(response.json()['messages']), 1)
        self.assertEqual(response.json()['messages'][0]['content'], 'Hello!')

    def test_send_message(self):
        url = reverse('send_message', args=[self.chat_room.id])
        response = self.client.post(url, json.dumps({'message': 'Hi back!'}), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(Message.objects.filter(content='Hi back!').exists())

    def test_chat_room_view_marks_messages_as_read(self):
        self.assertFalse(Message.objects.get(id=self.message.id).is_read)

        url = reverse('chat_room', args=[self.chat_room.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

    def test_start_chat_redirects_existing_room(self):
        url = reverse('start_chat', args=[self.user2.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)  # редирект
        self.assertIn(f'/chats/room/{response.url.split("/")[-2]}/', response.url)

    def test_start_chat_creates_new_room_if_not_exists(self):
        user3 = User.objects.create_user(username='user3', password='pass1234')
        url = reverse('start_chat', args=[user3.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChatRoom.objects.filter(user1=self.user1, user2=user3).exists())

    def test_my_chats_view(self):
        url = reverse('my_chats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user2.username)
        self.assertTemplateUsed(response, 'chats/my_chats.html')
