from ..forms import PostForm, CommentForm
from ..models import Post, Group, Comment
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class PostFormCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Test group 2',
            slug='Slug2',
            description='Test description 2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Тестовый пост',
            'image': 'posts/Ава3.jpg'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.last().text,
                        form_data['text'])
        new_post = Post.objects.last()
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.image, self.post.image)

    def test_post_edit_correct(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая запись с правками',
            'group': self.group2.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            id=self.post.pk,
        ).exists())
        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        new_group_response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug})
        )
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0)
        self.assertEqual(
            new_group_response.context['page_obj'].paginator.count, 1)


class CommentFormCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth3')
        cls.group = Group.objects.create(
            title='Группа',
            slug='Slug1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.form = CommentForm

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment_auth(self):
        """Проверка написания комментария авторизованным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Это комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        last_comment = Comment.objects.order_by('-pk')[0]
        self.assertEqual(last_comment.text, form_data['text'])

    def test_create_comment_not_auth(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Это второй комментарий'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
