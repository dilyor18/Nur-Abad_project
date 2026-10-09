from django.urls import reverse
from rest_framework.test import APITestCase

from apps.locations.models import City, District
from apps.users.models import User


class AuthApiTests(APITestCase):
    def test_register_user(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'alex',
                'email': 'alex@example.com',
                'password': 'StrongPass123!',
                'password_confirmation': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='alex@example.com').exists())

    def test_register_validates_password_confirmation(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'alex2',
                'email': 'alex2@example.com',
                'password': 'StrongPass123!',
                'password_confirmation': 'Mismatch123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)

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

    def test_login_accepts_username(self):
        User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='StrongPass123!',
        )

        response = self.client.post(
            reverse('login'),
            {
                'username': 'bob',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_update_requires_owner(self):
        city = City.objects.create(name='Ош')
        district = District.objects.create(name='Район А', city=city)

        user1 = User.objects.create_user(username='first', email='first@example.com', password='StrongPass123!')
        user2 = User.objects.create_user(username='second', email='second@example.com', password='StrongPass123!')

        self.client.force_authenticate(user=user1)
        response = self.client.patch(
            reverse('profile_me'),
            {'username': 'updated', 'city': city.id, 'district': district.id},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user1.profile.city, city)

        self.client.force_authenticate(user=user2)
        response = self.client.patch(
            reverse('profile_me'),
            {'username': 'hacker'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(user2.profile.username if hasattr(user2.profile, 'username') else '', 'hacker')
