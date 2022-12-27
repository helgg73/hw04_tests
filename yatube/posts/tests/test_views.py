from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

# Импортируем глобальные настройки
from django.conf import settings

from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostsPagesTests(TestCase):
    """Тест views приложения Posts"""
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
            author=PostsPagesTests.user,
            text='Тестовый пост',
            group=PostsPagesTests.group
        )

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр неавторизованного клиента.
        self.guest_client = Client()
        # Создаем авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)

    def test_pages_uses_correct_template(self):
        """Тестируемые views используют корректные шаблоны."""
        expected_templates = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostsPagesTests.user}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsPagesTests.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsPagesTests.post.pk}):
                'posts/create_post.html',
        }
        for name, expected in expected_templates.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, expected, f'views {name}')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        # Получаем данные со страницы группы
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsPagesTests.group.slug}
            )
        )
        # Проверяем пост со страницы группы
        self.assertEqual(response.context['page_obj'][0], PostsPagesTests.post)
        # Проверяем данные группы со страницы группы
        self.assertEqual(response.context['group'], PostsPagesTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        # Получаем данные со страницы пользователя
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostsPagesTests.user})
        )
        # Проверяем пост со страницы автора
        self.assertEqual(response.context['page_obj'][0], PostsPagesTests.post)
        # Проверяем данные автора
        self.assertEqual(response.context['author'], PostsPagesTests.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsPagesTests.post.pk}
        ))
        post = response.context['post']
        self.assertEqual(post, PostsPagesTests.post)

    def test_post_create_edit_pages_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        # Тестируемые страницы
        testing_pages = (
            f'/posts/{PostsPagesTests.post.pk}/edit/',
            '/create/'
        )
        for url in testing_pages:
            with self.subTest(url=url):
                # Получаем ответ страницы
                response = self.authorized_client.get(url)
                # Проверяем полученную форму
                self.assertIsInstance(
                    response.context['form'],
                    PostForm
                )
                # Проверяем is_edit
                self.assertIsNotNone(response.context['is_edit'])
                # Проверяем содержание формы
                if 'edit' in url:
                    self.assertEqual(
                        response.context['post_pk'],
                        PostsPagesTests.post.pk)
                    form = response.context['form']
                    self.assertEqual(
                        form['text'].value(),
                        PostsPagesTests.post.text
                    )
                    self.assertEqual(
                        form['group'].value(),
                        PostsPagesTests.post.group.pk
                    )

    def test_paginator(self):
        """Тест пажинатора"""
        # Постов больше лимита пажинатора
        COUNT_POST_OVER = 1
        # Страницы с пажинатором
        paginated_urls = (
            ['posts:index', None],
            ['posts:profile', PostsPagesTests.user],
            ['posts:group_list', PostsPagesTests.group.slug]
        )
        # Ожидаемое количество постов на страницах
        pages = (
            (1, settings.OBJECTS_ON_THE_PAGE),
            (2, COUNT_POST_OVER)
        )
        # Готовим данные для создания постов,
        # один создан в setUpClass
        bulk_data = []
        for index in range(settings.OBJECTS_ON_THE_PAGE + COUNT_POST_OVER - 1):
            bulk_data += [
                Post(
                    author=PostsPagesTests.user,
                    text=f'Текст поста {index}',
                    group=PostsPagesTests.group,
                )
            ]
        # Создаем посты
        Post.objects.bulk_create(bulk_data)
        # Проверяем количество постов на страницах
        for url, args in paginated_urls:
            for page, count in pages:
                with self.subTest(url=url, page=page):
                    if args:
                        response = self.authorized_client.get(
                            reverse(url, args=[args]),
                            {'page': page}
                        )
                    else:
                        response = self.authorized_client.get(
                            reverse(url),
                            {'page': page}
                        )
                    self.assertEqual(
                        len(response.context['page_obj']),
                        count)

    def test_correct_group_list(self):
        # Создаем новую группу
        self.group_new = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test_group_new',
            description='Тестовое новое описание',
        )
        # Создаем новый пост
        Post.objects.create(
            author=PostsPagesTests.user,
            text='Тестовый пост',
            group=PostsPagesTests.group
        )
        # Запрашиваем страницу новой группы
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                args=[self.group_new.slug]
            )
        )
        # Проверяем, что пост не попал на не нужную страницу
        self.assertEqual(
            len(response.context['page_obj']),
            0,
            'Неверная выборка на странице группы')
