from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Name2')
        cls.user2 = User.objects.create_user(username='Name3')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовая запись для тестов',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)
        self.url_names_all_user = [
            '/',
            '/group/Slug/',
            '/profile/Name2/',
            '/posts/1/',
        ]
        self.url_names_only_authorized = [
            '/posts/1/edit/',
            '/create/'
        ]

    def test_urls_anonymous(self):
        """Страницы доступна любому пользователю."""
        for address in self.url_names_all_user:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_redirect_anonymous(self):
        """Страницы перенаправят анонимного
           пользователя на страницу логина.
        """
        for address in self.url_names_only_authorized:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_edit_post_author(self):
        """Страница post_edit для автора использует правильный шаблон."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_edit_post_not_author(self):
        """Страница post_edit не для автора сделает редирект."""
        response = self.authorized_client2.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_not_found_404(self):
        """Страница не найдена."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_urls_uses_correct_template(self):
        """Страницы используют правильный шаблон"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/Slug/': 'posts/group_list.html',
            '/profile/Name2/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/nonexist-page/': 'core/404.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                cache.clear()
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
