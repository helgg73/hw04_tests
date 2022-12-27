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
        # Создаем пользователя
        cls.user = User.objects.create_user(username='JuniorTester')

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(CreatePageTest.user)

    def test_no_authorized_create_post(self):
        """Тестируем неавторизованное создание поста."""
        guest_client = Client()
        # Создаем форму для запроса POST
        form_data = {
            'text': 'Тестовый текст',
            'group': CreatePageTest.group.pk,
        }
        # Отправляем POST-запрос неавторизованным пользвателем
        response = guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )
        # Проверяем количество постов
        self.assertEqual(
            Post.objects.count(),
            0,
            'Пост добавлен неавторизованным пользователем'
        )

    def test_create_post(self):
        """Тестируем создание поста."""
        # Создаем форму для запроса POST
        form_data = {
            'text': 'Тестовый текст',
            'group': CreatePageTest.group.pk,
        }
        # Отправляем POST-запрос авторизованным пользвателем
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
            1,
            'Пост не добавлен'
        )
        # Проверяем содержание поста
        post = Post.objects.first()
        self.assertEqual(post.author, CreatePageTest.user, (
            'Ошибка создания поста, неверный автор'
        ))
        self.assertEqual(post.group, CreatePageTest.group, (
            'Ошибка создания поста, неверная группа'
        ))
        self.assertEqual(post.text, 'Тестовый текст', (
            'Ошибка создания поста, неверный текст'
        ))

    def test_edit_post(self):
        """Тестируем редактирование текста поста."""
        # Создаем пост
        post = Post.objects.create(
            author=CreatePageTest.user,
            text='Тестовый пост',
            group=CreatePageTest.group
        )
        # Создваем вторую группу
        self.new_group = Group.objects.create(
            title='Новая группа',
            slug='new_group',
            description='Новое описание',
        )
        # Готовим данные
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.new_group.pk
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            )
        )
        # Проверяем текст поста
        post = Post.objects.first()
        self.assertEqual(post.text, 'Отредактированный текст', (
            'Ошибка редактирования поста, неверный текст'
        ))
        # Проверяем группу поста
        self.assertEqual(post.group, self.new_group, (
            'Ошибка редактирования поста, неверная группа'
        ))
