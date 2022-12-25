from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    """Тест адресов и шаблонов страниц приложения Posts"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='JuniorTester')
        # Создаем тестовую группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        # Создаем тестовый пост
        cls.post = Post.objects.create(
            author=PostsURLTests.user,
            text='Тестовый пост',
            group=PostsURLTests.group
        )
        # Тестируемые страницы
        cls.homepage_url = '/'
        cls.group_url = f'/group/{PostsURLTests.group.slug}/'
        cls.profile_url = f'/profile/{PostsURLTests.post.author}/'
        cls.post_url = f'/posts/{PostsURLTests.post.pk}/'
        cls.post_edit_url = f'/posts/{PostsURLTests.post.pk}/edit/'
        cls.post_create = '/create/'
        cls.unexisting_url = 'unexisting_url'

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_public_pages(self):
        """Тест доступности публичных страниц"""
        expected_reason_phrase = {
            PostsURLTests.homepage_url: 'OK',
            PostsURLTests.group_url: 'OK',
            PostsURLTests.profile_url: 'OK',
            PostsURLTests.post_url: 'OK',
        }
        for value, expected in expected_reason_phrase.items():
            with self.subTest(url=value):
                response = self.guest_client.get(value)
                self.assertEquals(
                    response.reason_phrase,
                    expected,
                    f'страница {value} недоступна'
                )

    def test_restricted_pages(self):
        """Тест доступности неавторизованному пользователю
        требующих авторизации страниц"""
        expected_reason_phrase = {
            PostsURLTests.post_edit_url: 'Found',
            PostsURLTests.post_create: 'Found',
        }
        for value, expected in expected_reason_phrase.items():
            with self.subTest(url=value):
                response = self.guest_client.get(value)
                self.assertEquals(
                    response.reason_phrase,
                    expected,
                    f'страница {value} доступна без авторизации'
                )

    def test_unexisting_url(self):
        response = self.guest_client.get(PostsURLTests.unexisting_url)
        self.assertEquals(
            response.reason_phrase,
            'Not Found',
            f'Ошибка несуществующего url'
        )

    def test_pages_for_author_access(self):
        """Тест доступности для пользователя - автора"""
        expected_reason_phrase = {
            PostsURLTests.post_edit_url: 'OK',
            PostsURLTests.post_create: 'OK',
        }
        for value, expected in expected_reason_phrase.items():
            with self.subTest(url=value):
                response = self.authorized_client.get(value)
                self.assertEquals(
                    response.reason_phrase,
                    expected,
                    f'страница {value} не доступна автору'
                )

    def test_redirect_no_post_author(self):
        """Тест редиректа для не-автора поста"""
        self.user_new = User.objects.create_user(username='JuniorHacker')
        self.authorized_client_new = Client()
        self.authorized_client_new.force_login(self.user_new)
        response = self.authorized_client_new.get(
            PostsURLTests.post_edit_url, follow=True
        )
        self.assertRedirects(response, PostsURLTests.post_url)

    def test_templates(self):
        """Тест шаблонов"""
        expected_templates = {
            PostsURLTests.homepage_url: 'posts/index.html',
            PostsURLTests.group_url: 'posts/group_list.html',
            PostsURLTests.profile_url: 'posts/profile.html',
            PostsURLTests.post_url: 'posts/post_detail.html',
            PostsURLTests.post_edit_url: 'posts/create_post.html',
            PostsURLTests.post_create: 'posts/create_post.html',
        }
        for url, expected in expected_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response,
                    expected,
                    f'Неверный шаблон страницы {url}')

    def test_url_redirect_for_unauthorized_access(self):
        """Тест перенаправления неавторизованного пользователя"""
        expected_redirect = {
            PostsURLTests.post_edit_url: 
                f'/auth/login/?next={PostsURLTests.post_edit_url}',
            PostsURLTests.post_create:
                f'/auth/login/?next={PostsURLTests.post_create}',
        }

        for url, expected in expected_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, expected)
