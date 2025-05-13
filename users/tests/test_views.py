from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
import json
import base64
from moderation.models import UserBlocking
from listings.models import Listing

User = get_user_model()

class UsersViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', role='client')
        self.moderator = User.objects.create_user(username='moderator', password='modpass', role='moderator')
        self.support = User.objects.create_user(username='support', password='supportpass', role='support')
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass')
        self.image_data = self._create_test_image()

    def _create_test_image(self):
        img = Image.new('RGB', (100, 100), color='red')
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG')
        return SimpleUploadedFile('test_image.jpg', img_buffer.getvalue(), content_type='image/jpeg')

    def _login_user(self, username='testuser', password='testpass'):
        self.client.login(username=username, password=password)

    def test_user_manager_create_user(self):
        user = User.objects.create_user(username='newuser', password='newpass', role='client')
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.role, 'client')
        self.assertTrue(user.check_password('newpass'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_manager_create_superuser(self):
        superuser = User.objects.create_superuser(username='superuser', password='superpass')
        self.assertEqual(superuser.username, 'superuser')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.check_password('superpass'))

    def test_profile_view_unauthorized(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_get(self):
        self._login_user()
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_superuser_redirect(self):
        self._login_user('admin', 'adminpass')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:admin_profile'))

    def test_profile_view_update_avatar(self):
        self._login_user()
        response = self.client.post(reverse('users:profile'), {'avatar': self.image_data})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile'))
        updated_user = User.objects.get(id=self.user.id)
        self.assertIsNotNone(updated_user.avatar_base64)

    def test_register_user_form_validation(self):
        from users.forms import CustomUserCreationForm
        form_data = {
            'username': 'invalid@name',
            'tg_link': 'invalid_tg_link',
            'tel_number': '12345',
            'password1': 'Test12345',
            'password2': 'Test12345'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('tg_link', form.errors)
        self.assertIn('tel_number', form.errors)

    def test_register_user_success(self):
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'tg_link': 'https://t.me/newuser',
            'tel_number': '+996123456789',
            'password1': 'Test12345',
            'password2': 'Test12345'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='newuser')
        self.assertEqual(user.tg_link, 'https://t.me/newuser')
        self.assertEqual(user.tel_number, '+996123456789')

    def test_show_user_profile_self_redirect(self):
        self._login_user()
        response = self.client.get(reverse('users:another_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile'))

    def test_show_user_profile_moderator_block(self):
        self._login_user('moderator', 'modpass')
        response = self.client.post(
            reverse('users:another_profile', args=[self.user.id]),
            data=json.dumps({'reason_for_blocking': 'Test reason'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:another_profile', args=[self.user.id]))
        updated_user = User.objects.get(id=self.user.id)
        self.assertTrue(updated_user.is_blocked)
        blocking = UserBlocking.objects.get(user=updated_user)
        self.assertEqual(blocking.blocking_cause, 'Test reason')

    def test_show_user_profile_support_unblock(self):
        self.user.is_blocked = True
        self.user.save()
        self._login_user('support', 'supportpass')
        response = self.client.post(reverse('users:another_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:another_profile', args=[self.user.id]))
        updated_user = User.objects.get(id=self.user.id)
        self.assertFalse(updated_user.is_blocked)

    def test_show_user_profile_support_blocked_user(self):
        self.user.is_blocked = True
        self.user.save()
        UserBlocking.objects.create(user=self.user, blocking_cause='Test reason')
        self._login_user('support', 'supportpass')
        response = self.client.get(reverse('users:another_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/another_profile.html')
        self.assertTrue(response.context['user'].is_blocked)
        self.assertEqual(response.context['blocking'].blocking_cause, 'Test reason')

    def test_show_user_profile_support_blocked_listings(self):
        self._login_user('support', 'supportpass')
        listing = Listing.objects.create(user=self.user, title='Test Listing', is_blocked=True)
        response = self.client.get(reverse('users:another_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/another_profile.html')
        self.assertTrue(response.context['has_blocked_listings'])

    def test_change_password_view_get(self):
        self._login_user()
        response = self.client.get(reverse('users:change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/change_password.html')

    def test_change_password_invalid_json(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data='invalid_json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Неверный формат данных'})

    def test_change_password_missing_fields(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({'old_password': 'testpass'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Все поля обязательны для заполнения'})

    def test_change_password_mismatched_new_passwords(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({
                'old_password': 'testpass',
                'new_password1': 'NewPass123',
                'new_password2': 'NewPass456'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Новые пароли не совпадают'})

    def test_change_password_short_new_password(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({
                'old_password': 'testpass',
                'new_password1': 'Short1',
                'new_password2': 'Short1'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Новый пароль должен содержать минимум 8 символов'})

    def test_change_password_same_as_old(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({
                'old_password': 'testpass',
                'new_password1': 'testpass',
                'new_password2': 'testpass'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Новый пароль не должен совпадать со старым'})

    def test_change_password_no_uppercase(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({
                'old_password': 'testpass',
                'new_password1': 'newpass123',
                'new_password2': 'newpass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Пароль должен содержать хотя бы одну заглавную букву'})

    def test_change_password_no_digit(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({
                'old_password': 'testpass',
                'new_password1': 'NewPassword',
                'new_password2': 'NewPassword'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Пароль должен содержать хотя бы одну цифру'})

    def test_change_password_incorrect_old_password(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({
                'old_password': 'wrongpass',
                'new_password1': 'NewPass123',
                'new_password2': 'NewPass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Неверный старый пароль'})

    def test_change_password_success(self):
        self._login_user()
        response = self.client.post(
            reverse('users:change_password'),
            data=json.dumps({
                'old_password': 'testpass',
                'new_password1': 'NewPass123',
                'new_password2': 'NewPass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': 'Пароль успешно изменен'})
        updated_user = User.objects.get(id=self.user.id)
        self.assertTrue(updated_user.check_password('NewPass123'))

    def tearDown(self):
        User.objects.all().delete()