from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Административная панель
    path('admin/', admin.site.urls),
    # Переопределение стандартных шаблонов авторизации
    path('auth/', include('users.urls', namespace='users')),
    # Стандартные шаблоны авторизации
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    # импорт правил из приложения posts
    path('', include('posts.urls', namespace='posts')),
]
