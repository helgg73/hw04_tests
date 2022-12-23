from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    """Тест адресов и шаблонов страниц приложения Posts"""
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем двух авторизованых клиентов
        self.user = User.objects.create_user(username='JuniorTester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.create_user(username='JuniorHacker')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        # Создаем тестовую группу
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        # Создаем тестовый пост
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        # Тестируемые страницы
        self.homepage = '/'
        self.group_url = f'/group/{self.group.slug}/'
        self.profile_url = f'/profile/{self.post.author}/'
        self.post_url = f'/posts/{self.post.pk}/'
        self.post_edit_url = f'/posts/{self.post.pk}/edit/'
        self.post_create = '/create/'
        self.unexisting_url = 'unexisting_url'

    def test_pages_for_unauthorized_access(self):
        """Тест доступности для неавторизованного пользователя"""

        expected_reason_phrase = {
            self.homepage: 'OK',
            self.group_url: 'OK',
            self.profile_url: 'OK',
            self.post_url: 'OK',
            self.post_edit_url: 'Found',
            self.post_create: 'Found',
            self.unexisting_url: 'Not Found',
        }

        for value, expected in expected_reason_phrase.items():
            with self.subTest(url=value):
                response = self.guest_client.get(value)
                self.assertEquals(
                    response.reason_phrase,
                    expected,
                    f'страница {value} недоступна'
                )

    def test_pages_for_authorized_access(self):
        """Тест доступности для авторизованного пользователя"""
        expected_reason_phrase = {
            self.post_edit_url: 'Found',
            self.post_create: 'OK',
        }

        for value, expected in expected_reason_phrase.items():
            with self.subTest(url=value):
                response = self.authorized_client2.get(value)
                self.assertEquals(
                    response.reason_phrase,
                    expected,
                    f'страница {value} недоступна'
                )

    def test_edit_post_for_author(self):
        """Тест доступности редактирования для автора поста"""
        response = self.authorized_client.get(self.post_edit_url)
        self.assertEquals(
            response.reason_phrase,
            'OK',
            'Страница редактирвоания поста недоступна'
        )

    def test_templates(self):
        """Тест шаблонов"""

        expected_templates = {
            self.homepage: 'posts/index.html',
            self.group_url: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_url: 'posts/post_detail.html',
            self.post_edit_url: 'posts/create_post.html',
            self.post_create: 'posts/create_post.html',
        }

        for url, expected in expected_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, expected, f'страница {url}')

    def test_url_redirect(self):
        response = self.guest_client.get(self.post_edit_url, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={self.post_edit_url}'
        )
        response = self.guest_client.get(self.post_create, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={self.post_create}'
        )
        response = self.authorized_client2.get(self.post_edit_url, follow=True)
        self.assertRedirects(
            response, self.post_url
        )
