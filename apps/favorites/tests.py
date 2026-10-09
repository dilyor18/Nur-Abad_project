from django.urls import reverse
from rest_framework.test import APITestCase

from apps.ads.models import Ad, Category
from apps.locations.models import City, District
from apps.users.models import User


class FavoriteApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', email='buyer@example.com', password='StrongPass123!')
        self.seller = User.objects.create_user(username='seller', email='seller@example.com', password='StrongPass123!')
        self.city = City.objects.create(name='Ош')
        self.district = District.objects.create(name='Район А', city=self.city)
        self.category = Category.objects.create(name='Электроника')
        self.ad = Ad.objects.create(
            author=self.seller,
            category=self.category,
            city=self.city,
            district=self.district,
            title='iPhone 15',
            description='New smartphone',
            price='40000.00',
            condition=Ad.CONDITION_NEW,
            status=Ad.STATUS_ACTIVE,
        )

    def test_add_get_and_delete_favorite(self):
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(reverse('favorites-list'), {'ad': self.ad.id}, format='json')
        self.assertEqual(create_response.status_code, 201)

        list_response = self.client.get(reverse('favorites-list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)

        delete_response = self.client.delete(reverse('favorite-detail', args=[create_response.data['id']]))
        self.assertEqual(delete_response.status_code, 204)

    def test_cannot_favorite_own_ad_or_duplicate(self):
        self.client.force_authenticate(user=self.seller)
        self_response = self.client.post(reverse('favorites-list'), {'ad': self.ad.id}, format='json')
        self.assertEqual(self_response.status_code, 400)

        self.client.force_authenticate(user=self.user)
        first = self.client.post(reverse('favorites-list'), {'ad': self.ad.id}, format='json')
        second = self.client.post(reverse('favorites-list'), {'ad': self.ad.id}, format='json')
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
