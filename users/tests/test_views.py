import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from users.models import User
from listings.models import Listing
from moderation.models import UserBlocking
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


class UserProfileTests(TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'password123',
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.user_staff = get_user_model().objects.create_user(
            username='supportuser',
            password='password123',
            role='support'
        )
        self.user_moderator = get_user_model().objects.create_user(
            username='moderatoruser',
            password='password123',
            role='moderator'
        )
        self.client.login(username='testuser', password='password123')

    def test_profile_view(self):
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('login'))

    def test_register_user_with_correct_password(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser',
            'password1': 'newpassword@123S',
            'password2': 'newpassword@123S',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('login'))

    def test_show_user_profile_for_moderator(self):
        url = reverse('users:another_profile', kwargs={'user_id': self.user.id})
        self.client.login(username='moderatoruser', password='password123')
        response = self.client.post(url, json.dumps({
            'reason_for_blocking': 'Inappropriate behavior'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_blocked)

        blocking = UserBlocking.objects.filter(user=self.user).first()
        self.assertIsNotNone(blocking)
        self.assertEqual(blocking.blocking_cause, 'Inappropriate behavior')

    def test_show_user_profile_for_support(self):
        url = reverse('users:another_profile', kwargs={'user_id': self.user.id})
        self.client.login(username='supportuser', password='password123')

        self.user.is_blocked = True
        self.user.save()

        response = self.client.post(url)
        self.assertRedirects(response, url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_blocked)

    def test_profile_avatar_upload(self):
        url = reverse('users:profile')
        self.client.login(username='testuser', password='password123')

        image = Image.new('RGB', (100, 100), color='red')
        image_content = BytesIO()
        image.save(image_content, format='PNG')
        image_content.seek(0)

        avatar_file = SimpleUploadedFile(
            name='avatar.png',
            content=image_content.read(),
            content_type='image/png'
        )

        response = self.client.post(url, {'avatar': avatar_file})

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.avatar_base64)

    def test_show_user_profile_when_user_is_blocked(self):
        url = reverse('users:another_profile', kwargs={'user_id': self.user.id})
        self.client.login(username='supportuser', password='password123')

        self.user.is_blocked = True
        self.user.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/another_profile.html')

        blocking = UserBlocking.objects.filter(user=self.user).order_by('-created_at').first()
        self.assertEqual(response.context['blocking'], blocking)
