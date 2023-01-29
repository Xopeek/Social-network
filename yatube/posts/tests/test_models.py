from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_objects_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task_group = PostModelTest.group
        task_post = PostModelTest.post
        object_name_group = task_group.title
        object_name_post = task_post.text[:15]
        self.assertEqual(object_name_group, str(task_group))
        self.assertEqual(object_name_post, str(task_post))

    def test_text_label(self):
        """Проверяем, что у моделей правильно работает verbose_name."""
        task = PostModelTest.post
        verbose = task._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст записи')

    def test_text_help_text(self):
        """Проверяем, что у моделей правильно работает help_text."""
        task = PostModelTest.post
        help_text = task._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст записи')
