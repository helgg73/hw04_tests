from django import forms
from posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        # Эта форма будет работать с моделью Post
        model = Post
        # Поля модели, которые должны отображаться в веб-форме
        fields = ('text', 'group')
