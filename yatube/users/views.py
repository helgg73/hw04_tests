from django.views.generic import CreateView
# Функция reverse_lazy позволяет получить URL по параметрам функции path()
from django.urls import reverse_lazy
# Импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/signup.html'
