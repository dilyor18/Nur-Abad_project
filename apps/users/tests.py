from django.urls import reverse
from rest_framework.test import APITestCase

from apps.users.models import User


class AuthApiTests(APITestCase):
    def test_register_user(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'alex',
                'email': 'alex@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='alex@example.com').exists())

    def test_login_returns_tokens(self):
        User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='StrongPass123!',
        )

        response = self.client.post(
            reverse('login'),
            {
                'email': 'alice@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
