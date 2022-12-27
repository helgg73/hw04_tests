from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersURLTests(TestCase):
    """Тест адресов и шаблонов страниц приложения Users"""
    @classmethod
    def setUp(self):
        # Создаём экземпляр неавторизованного клиента.
        self.guest_client = Client()
        # Создаем авторизованого клиента
        self.user = User.objects.create_user(username='JuniorTester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # Тестируемые страницы
        self.signup_url = '/auth/signup/'
        self.logging_out_url = '/auth/logout/'
        self.login_url = '/auth/login/'
        self.password_reset_url = '/auth/password_reset/'
        self.password_reset_done_url = '/auth/password_reset/done/'
        self.password_change_url = '/auth/password_change/'
        self.password_change_done_url = '/auth/password_change/done/'
        self.password_reset_confirm_url = '/auth/reset/<uidb64>/<token>/'
        self.password_reset_complete_url = '/auth/reset/done/'

    def test_pages_for_unauthorized_access(self):
        """Тест доступности для неавторизованного пользователя"""
        expected_status_code = {
            self.signup_url: 200,
            self.logging_out_url: 200,
            self.login_url: 200,
            self.password_reset_url: 200,
            self.password_reset_done_url: 200,
            self.password_change_url: 302,
            self.password_change_done_url: 302,
            self.password_reset_confirm_url: 200,
            self.password_reset_complete_url: 200,
        }

        for value, expected in expected_status_code.items():
            with self.subTest(url=value):
                response = self.guest_client.get(value)
                self.assertEqual(
                    response.status_code,
                    expected,
                    f'страница {value}'
                )

    def test_pages_for_authorized_access(self):
        """Тест доступности для авторизованного пользователя"""
        expected_status_code = {
            self.password_change_url: 200,
            self.password_change_done_url: 200,
        }

        for value, expected in expected_status_code.items():
            with self.subTest(url=value):
                response = self.authorized_client.get(value)
                self.assertEqual(
                    response.status_code,
                    expected, f'страница {value}'
                )

    def test_url_redirect(self):
        response = self.guest_client.get(self.password_change_url, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={ self.password_change_url}'
        )
        response = self.guest_client.get(
            self.password_change_done_url,
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next={self.password_change_done_url}'
        )
