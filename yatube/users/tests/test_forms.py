from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class SingUpTestUser(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        new_user_count = User.objects.count()
        form_data = {
            'first_name': 'Name User',
            'last_name': 'Last Name',
            'username': 'NikName',
            'email': 'test_email@gmail.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        new_user = User.objects.last()
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), new_user_count + 1)
        self.assertEqual(new_user.username, form_data['username'])
