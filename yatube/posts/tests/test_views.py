from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    """Тест шаблонов views-классов приложения Posts"""
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр неавторизованного клиента.
        self.guest_client = Client()
        # Создаем двух авторизованых клиентов
        self.user = User.objects.create_user(username='JuniorTester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.create_user(username='HackerJunior')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        # Создаем тестовую группу
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        # Создаем вторую тестовую группу
        self.group2 = Group.objects.create(
            title='Тестовая вторая группа',
            slug='test_group2',
            description='Тестовое второе описание',
        )
        # Создаем первый тестовый пост
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        # Создаем по step*2 постов на автора в двух группах
        # и step без группы
        steps = 7
        for i in range(steps):
            Post.objects.create(
                author=self.user,
                text='Тестовый пост JuniorTester в первой группе',
                group=self.group
            )
            Post.objects.create(
                author=self.user2,
                text='Тестовый пост JuniorHacker в первой группе',
                group=self.group
            )
            Post.objects.create(
                author=self.user,
                text='Тестовый пост JuniorTester во второй группе',
                group=self.group2
            )
            Post.objects.create(
                author=self.user2,
                text='Тестовый пост JuniorHacker во второй группе',
                group=self.group2
            )
            Post.objects.create(
                author=self.user,
                text='Тестовый пост JuniorTester без группы',
                group=None
            )

        self.posts = Post.objects.select_related('group', 'author')

    def test_pages_uses_correct_template(self):
        """Тестируемые views используют корректные шаблоны."""
        expected_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
        }
        for name, expected in expected_templates.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, expected, f'views {name}')

#    Непредсказуемо, какой пост окажется первым в выдаче
#    def test_home_page_show_correct_context(self):
#        """Шаблон index сформирован с правильным контекстом."""
#        response = self.guest_client.get(reverse('posts:index'))
#        first_post = response.context['page_obj'][0]
#        self.assertEqual(first_post.text, self.post.text)
#        self.assertEqual(first_post.author, self.post.author)
#        self.assertEqual(first_post.group, self.post.group)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        page_obj = response.context['page_obj']
        for post in page_obj:
            with self.subTest(post=post):
                self.assertEqual(post.group, self.group, (
                    f'Ошибка в выводе группы {self.group}')
                )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        page_obj = response.context['page_obj']
        for post in page_obj:
            with self.subTest(post=post):
                self.assertEqual(post.author, self.user, (
                    f'Ошибка в выводе профиля {self.user}')
                )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        some_post = response.context['post']
        self.assertEqual(some_post.text, self.post.text)
        self.assertEqual(some_post.author, self.post.author)
        self.assertEqual(some_post.group, self.post.group)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        user = self.post.author
        authorized_client = Client()
        authorized_client.force_login(user)
        response = authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        )
        )
        form_fields_type = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField, поля модели типа
            # ForeignKey в ModelChoiceField
            'group': forms.models.ModelChoiceField,
        }
        # Проверяем тип полей контекста
        for value, expected in form_fields_type.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        # Проверяем содержание полей контекста
        self.assertEqual(response.context['is_edit'], True)
        self.assertEqual(response.context['post_pk'], self.post.pk)
        # Проверяем предустановленнное значение формы.
#        text_initial = response.context['form'].fields['group'].initial
        text_initial = response.context['form'].initial['text']
        self.assertEqual(text_initial, self.post.text)
        group_initial = response.context['form'].initial['group']
        self.assertEqual(group_initial, self.post.group.pk)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields_type = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField, поля модели типа
            # ForeignKey в ModelChoiceField
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields_type.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_first_page_paginator(self):
        """Тест пажинатора страницы index."""
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно
        # OBJECTS_ON_THE_PAGE.
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=4')
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_group_list_page_paginator(self):
        """Тест пажинатора страницы group_list."""
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug})
        )
        # Проверка: количество постов на первой странице index
        # равно 10, на последней - 5
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_page_paginator(self):
        """Тест пажинатора страницы profile."""
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user2})
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user2}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 4)
