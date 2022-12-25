from django.shortcuts import render, get_object_or_404
from posts.models import Post, Group
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
# Импортируем глобальные настройки
from django.conf import settings
# Импортируем класс формы, чтобы сослаться на неё во view-классе
from posts.forms import PostForm


def paginate_page(request, posts):
    # Получаем набор из OBJECTS_ON_THE_PAGE записей
    # для страницы page из request
    page_number = request.GET.get('page')
    paginator = Paginator(posts, settings.OBJECTS_ON_THE_PAGE)
    return paginator.get_page(page_number)


def index(request):
    # Получаем выборку из всех объектов модели Post,
    # подразумевается, что сортировка по полю pub_date
    # по убыванию прописана в классе Meta модели.
    # Сразу запрашиваем связанные объекты group и author
    posts = Post.objects.select_related('group', 'author')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginate_page(request, posts)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    group = get_object_or_404(Group, slug=slug)
    # .posts - related_name поля group класса Post
    posts = group.posts.select_related('author')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginate_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginate_page(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/post_detail.html', {'post': post})


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not post.author == request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_pk': post_id
    }
    return render(request, 'posts/create_post.html', context)
