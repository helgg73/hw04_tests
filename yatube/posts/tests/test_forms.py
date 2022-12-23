from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class CreatePageTest(TestCase):
    """Тест создания и редактирования пользователем объекта Post"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем тестовую группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        # Создаем вторую тестовую группу
        cls.group2 = Group.objects.create(
            title='Тестовая группа',
            slug='test_group2',
            description='Тестовое описание',
        )
        # Создаем пользователя
        cls.user = User.objects.create_user(username='JuniorTester')

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(CreatePageTest.user)

    def test_create_post(self):
        """Тестируем создание поста."""
        # Проверяем количество постов
        post_count = Post.objects.count()
        # Создаем форму для запроса POST
        form_data = {
            'text': 'Тестовый текст',
            'group': CreatePageTest.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': CreatePageTest.user}
            )
        )
        # Проверяем количество постов
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'Пост не добавлен'
        )

    def test_edit_post(self):
        """Тестируем редактирование текста поста."""
        # Создаем пост
        post = Post.objects.create(
            author=CreatePageTest.user,
            text='Тестовый пост',
            group=CreatePageTest.group
        )
        post_id = post.pk
        # Готовим данные
        form_data = {
            'text': 'Отредактированный текст',
            'group': CreatePageTest.group2.pk
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}
            )
        )
        # Проверяем текст поста
        post = Post.objects.get(pk=post_id)
        self.assertEqual(post.text, 'Отредактированный текст')
        # Проверяем группу поста
        self.assertEqual(post.group, CreatePageTest.group2)
