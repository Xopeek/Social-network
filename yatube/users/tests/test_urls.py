from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Users')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_names_all_users = [
            '/auth/logout/',
            '/auth/password_reset/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/',
            '/auth/login/',
            '/auth/signup/'
        ]
        self.url_names_only_auth_users = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]

    def test_users_anonymous(self):
        for address in self.url_names_all_users:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_redirect_anonymous(self):
        for address in self.url_names_only_auth_users:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_only_auth_users(self):
        for address in self.url_names_only_auth_users:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'users/logged_out.html': '/auth/logout/',
            'users/login.html': '/auth/login/',
            'users/password_reset_complete.html':
                '/auth/reset/done/',
            'users/password_reset_confirm.html':
                '/auth/reset/<uidb64>/<token>/',
            'users/password_reset_done.html':
                '/auth/password_reset/done/',
            'users/password_reset_form.html':
                '/auth/password_reset/',
            'users/signup.html': '/auth/signup/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
