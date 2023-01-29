from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Post, Group, Follow


User = get_user_model()


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Name')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для тестов',
            group=cls.group,
            image='posts/Ава3.jpg'
        )
        posts = []
        for i in range(1, 11):
            post = Post(
                author=cls.user,
                text='Тестовая запись',
                group=cls.group,
                image='posts/Ава3.jpg'
            )
            posts.append(post)
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

    def test_pages_uses_correct_template(self):
        """URL-адреса используют соответствующий шаблон"""
        self.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list', kwargs={'slug': 'Slug'})):
                'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': 'Name'})):
                'posts/profile.html',
            (reverse('posts:post_detail', kwargs={'post_id': 1})):
                'posts/post_detail.html',
            (reverse('posts:post_edit', kwargs={'post_id': 1})):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
         и правильная картинка."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        post_list = list(Post.objects.all()[:10])
        post_image = list(Post.objects.filter(image=self.post.image)[:10])
        self.assertEqual(list(response.context['page_obj']), post_list)
        self.assertEqual(list(response.context['page_obj']), post_image)

    def test_group_post_correct_contex(self):
        """Шаблон group_list сформирован с правильным контекстом
         и правильная картинка."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        post_group_list = list(Post.objects.filter(
            group_id=self.group.id,
            image=self.post.image
        )[:10])
        self.assertEqual(list(response.context['page_obj']), post_group_list)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом
         и правильная картинка."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Name'})
        )
        post_profile = list(Post.objects.filter(author_id=self.user.id,
                                                image=self.post.image)[:10])
        self.assertEqual(list(response.context['page_obj']), post_profile)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_old_create_post_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_create_post_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_show_group_correct(self):
        """Группа правильно отображается на страницах."""
        cache.clear()
        form_fields = {
            reverse('posts:index'): Post.objects.filter(
                group=self.post.group
            )[0],
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                Post.objects.filter(group=self.post.group)[0],
            reverse('posts:profile', kwargs={'username': self.post.author}):
                Post.objects.filter(group=self.post.group)[0],
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                cache.clear()
                self.assertIn(expected, form_field)

    def test_group_not_in_mistake_group(self):
        """Пост не попал в другую группу."""
        form_fields = {
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                Post.objects.exclude(group=self.post.group)
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)

    def test_paginator_correct(self):
        """Пагинатор правильно отображает страницы."""
        cache.clear()
        paginator_reverse = {
            'index': reverse('posts:index'),
            'profile': reverse('posts:profile',
                               kwargs={'username': self.post.author})
        }
        for place, page in paginator_reverse.items():
            with self.subTest(place=place):
                response_page_1 = self.authorized_client.get(page)
                response_page_2 = self.authorized_client.get(page + '?page=2')
                self.assertEqual(len(response_page_1.context['page_obj']), 10)
                self.assertEqual(len(response_page_2.context['page_obj']), 1)

    def test_cache_index_page(self):
        """Проверка сохранения кэша для index"""
        new_post = Post.objects.create(
            author=self.user,
            text='Проверка кэша'
        )
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertIn(new_post, response.context['page_obj'])
        new_post.delete()
        new_response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, new_response.content)


class FollowTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='FollowUser')
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Test Group',
            slug='FollowSlug',
            description='TestDescr'
        )
        cls.post = Post.objects.create(
            text='Test Text Follow',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.author_user = Client()
        self.author_user.force_login(self.author)
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_authorized_author(self):
        """Проверка, что авторизованный пользователь может подписаться."""
        cache.clear()
        response = self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={
                'username': self.author.username
            })
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
        follow = Follow.objects.latest('id')
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, self.author)
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.author.username}))

    def test_unfollow_authorized_author(self):
        """Проверка, что авторизованный пользователь может отписаться."""
        Follow.objects.create(
            user=self.user, author=self.author
        )
        response = self.authorized_client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username})
        )
        self.assertEqual(Follow.objects.count(), 0)
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.author.username}))

    def test_correct_context_follow(self):
        """Проверка, что новая запись появляется у подписчиков."""
        Post.objects.create(
            author=self.author,
            text='NNNN',
        )
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].author, self.author)

    def test_correct_context_unfollow(self):
        """Проверка, что у пользователя не появляется запись,
         тех на кого он не подписан."""
        Post.objects.create(
            author=self.author,
            text='ASDA'
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)
