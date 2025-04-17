from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTest(TestCase):

    def test_create_user(self):
        username = 'testuser'
        password = 'password123'
        user = get_user_model().objects.create_user(username=username, password=password)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        username = 'adminuser'
        password = 'adminpassword'
        user = get_user_model().objects.create_superuser(username=username, password=password)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_username(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(username='', password='password123')

    def test_create_user_with_invalid_role(self):
        user = get_user_model().objects.create_user(username='testuser2', password='password123', role='admin')
        self.assertEqual(user.role, 'admin')

    def test_user_str_method(self):
        user = get_user_model().objects.create_user(username='testuser3', password='password123')
        self.assertEqual(str(user), 'testuser3')

    def test_create_user_with_optional_fields(self):
        user = get_user_model().objects.create_user(
            username='testuser4', password='password123', tg_link='https://t.me/test', tel_number='1234567890'
        )
        self.assertEqual(user.tg_link, 'https://t.me/test')
        self.assertEqual(user.tel_number, '1234567890')

    def test_user_avatar_base64(self):
        avatar_data = 'data:image/png;base64,abc123'
        user = get_user_model().objects.create_user(
            username='testuser5', password='password123', avatar_base64=avatar_data
        )
        self.assertEqual(user.avatar_base64, avatar_data)

    def test_blocked_user(self):
        user = get_user_model().objects.create_user(username='blockeduser', password='password123', is_blocked=True)
        self.assertTrue(user.is_blocked)

    def test_user_permissions(self):
        user = get_user_model().objects.create_user(username='testuser6', password='password123')
        self.assertFalse(user.has_perm('some_permission'))
        self.assertFalse(user.has_module_perms('some_app'))
