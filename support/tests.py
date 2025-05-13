from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Appeal, AppealPicture, AppealStatus
from django.utils.timezone import now
import base64
from io import BytesIO
from PIL import Image

class SupportViewsTestCase(TestCase):
    def setUp(self):
        # Настройка тестового клиента и пользователей
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', role='user')
        self.support_user = User.objects.create_user(username='supportuser', password='testpass', role='support')
        self.image_data = self._create_test_image()
        # Установка текущего времени для тестов
        self.current_time = now()  # 03:35 PM +06, 13 мая 2025

    def _create_test_image(self):
        # Создание тестового изображения для загрузки
        img = Image.new('RGB', (100, 100), color='red')
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG')
        return base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    def _login_user(self, username='testuser', password='testpass'):
        self.client.login(username=username, password=password)

    def test_support_view_unauthorized(self):
        # Проверка, что неавторизованный пользователь перенаправляется
        response = self.client.get(reverse('support'))
        self.assertEqual(response.status_code, 302)

    def test_support_view_user_access(self):
        # Проверка доступа обычного пользователя
        self._login_user()
        response = self.client.get(reverse('support'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/support.html')

    def test_support_view_support_role_redirect(self):
        # Проверка, что пользователь с ролью support перенаправляется
        self._login_user('supportuser', 'testpass')
        response = self.client.get(reverse('support'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('appeals'))

    def test_support_view_post_success(self):
        # Проверка успешного создания обращения
        self._login_user()
        response = self.client.post(reverse('support'), {
            'message': 'Тестовое обращение',
            'file': [self.image_data]  # Симуляция файла (Base64)
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ваше обращение успешно получено')
        self.assertEqual(Appeal.objects.count(), 1)
        appeal = Appeal.objects.first()
        self.assertEqual(appeal.user, self.user)
        self.assertEqual(appeal.text, 'Тестовое обращение')
        self.assertEqual(appeal.closed, False)
        self.assertEqual(AppealPicture.objects.count(), 1)
        picture = AppealPicture.objects.first()
        self.assertEqual(picture.appeal, appeal)
        self.assertEqual(picture.image_base64, self.image_data)

    def test_support_view_post_empty_message(self):
        # Проверка обработки пустого сообщения
        self._login_user()
        response = self.client.post(reverse('support'), {'message': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сообщение не может быть пустым')
        self.assertEqual(Appeal.objects.count(), 0)

    def test_show_appeals_view(self):
        # Проверка отображения списка обращений
        self._login_user('supportuser', 'testpass')
        appeal = Appeal.objects.create(user=self.user, text='Тест', closed=False)
        appeal.last_answered_at = self.current_time  # Установка текущего времени
        appeal.save()
        response = self.client.get(reverse('appeals'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/appeals.html')
        self.assertEqual(len(response.context['appeals']), 1)
        self.assertEqual(response.context['appeals'][0], appeal)

    def test_work_with_appeal_get(self):
        # Проверка GET-запроса для работы с обращением
        self._login_user('supportuser', 'testpass')
        appeal = Appeal.objects.create(user=self.user, text='Тест', closed=False)
        AppealPicture.objects.create(appeal=appeal, image_base64=self.image_data)
        response = self.client.get(reverse('work_with_appeal', args=[appeal.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/work_with_appeal.html')
        self.assertEqual(response.context['appeal'], appeal)
        self.assertEqual(list(response.context['pictures']), list(appeal.pictures.all()))
        self.assertEqual(list(response.context['statuses']), [])

    def test_work_with_appeal_post_close(self):
        # Проверка закрытия обращения
        self._login_user('supportuser', 'testpass')
        appeal = Appeal.objects.create(user=self.user, text='Тест', closed=False)
        response = self.client.post(reverse('work_with_appeal', args=[appeal.id]), {'close_appeal': '1'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('appeals'))
        updated_appeal = Appeal.objects.get(id=appeal.id)
        self.assertTrue(updated_appeal.closed)
        self.assertEqual(AppealStatus.objects.count(), 1)
        status = AppealStatus.objects.first()
        self.assertEqual(status.appeal, appeal)
        self.assertEqual(status.comment, "Обращение закрыто")

    def test_work_with_appeal_post_comment(self):
        # Проверка добавления комментария
        self._login_user('supportuser', 'testpass')
        appeal = Appeal.objects.create(user=self.user, text='Тест', closed=False)
        comment_text = 'Тестовый комментарий'
        response = self.client.post(reverse('work_with_appeal', args=[appeal.id]), {
            'comment': comment_text
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('work_with_appeal', args=[appeal.id]))
        updated_appeal = Appeal.objects.get(id=appeal.id)
        self.assertTrue(updated_appeal.last_answered_at <= self.current_time.replace(second=0, microsecond=0))
        self.assertEqual(AppealStatus.objects.count(), 1)
        status = AppealStatus.objects.first()
        self.assertEqual(status.appeal, appeal)
        self.assertEqual(status.comment, comment_text)

    def tearDown(self):
        # Очистка после тестов
        User.objects.all().delete()
        Appeal.objects.all().delete()
        AppealPicture.objects.all().delete()
        AppealStatus.objects.all().delete()

if __name__ == '__main__':
    import django
    django.setup()
    unittest.main()