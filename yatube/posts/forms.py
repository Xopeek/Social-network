from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите группу',
            'image': 'Добавьте картинку'
        }
        help_texts = {
            'text': 'Текст вашей записи',
            'group': 'Из уже существующих',
            'image': 'Загрузите'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Введите текст комментария'
        }
        help_texts = {
            'text': 'Текст вашего комментария'
        }
