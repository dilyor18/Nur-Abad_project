import io

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.ads.models import Ad, Category
from apps.locations.models import City, District
from apps.users.models import User


class AdApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller', email='seller@example.com', password='StrongPass123!')
        self.other_user = User.objects.create_user(username='buyer', email='buyer@example.com', password='StrongPass123!')
        self.category = Category.objects.create(name='Автомобили')
        self.city = City.objects.create(name='Ош')
        self.district = District.objects.create(name='Район А', city=self.city)

    def test_create_ad_sets_author_and_active_status(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('ads-list'),
            {
                'title': 'BMW X5',
                'description': 'Good condition',
                'price': '25000.00',
                'category': self.category.id,
                'city': self.city.id,
                'district': self.district.id,
                'condition': Ad.CONDITION_USED,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], self.user.username)
        self.assertEqual(response.data['status'], Ad.STATUS_ACTIVE)
        self.assertEqual(Ad.objects.get(pk=response.data['id']).author, self.user)

    def test_anonymous_user_can_create_ad(self):
        response = self.client.post(
            reverse('ads-list'),
            {
                'title': 'Anonymous ad',
                'description': 'No login required',
                'price': '2300.00',
                'category': self.category.id,
                'city': self.city.id,
                'district': self.district.id,
                'condition': Ad.CONDITION_NEW,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], 'guest')
        self.assertTrue(Ad.objects.filter(pk=response.data['id']).exists())

    def test_district_must_match_city(self):
        city_2 = City.objects.create(name='Бишкек')
        district_2 = District.objects.create(name='Район Б', city=city_2)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('ads-list'),
            {
                'title': 'Wrong location',
                'description': 'Bad mapping',
                'price': '1000.00',
                'category': self.category.id,
                'city': self.city.id,
                'district': district_2.id,
                'condition': Ad.CONDITION_USED,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('district', response.data)

    def test_negative_price_is_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('ads-list'),
            {
                'title': 'Bad price',
                'description': 'Wrong price',
                'price': '-100',
                'category': self.category.id,
                'city': self.city.id,
                'district': self.district.id,
                'condition': Ad.CONDITION_NEW,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_only_author_can_update_or_delete_ad(self):
        ad = Ad.objects.create(
            author=self.user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='Old title',
            description='Old description',
            price='1200.00',
            condition=Ad.CONDITION_USED,
            status=Ad.STATUS_ACTIVE,
        )

        self.client.force_authenticate(user=self.user)
        patch_response = self.client.patch(
            reverse('ad-detail', args=[ad.id]),
            {'title': 'New title'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data['title'], 'New title')

        delete_response = self.client.delete(reverse('ad-detail', args=[ad.id]))
        self.assertEqual(delete_response.status_code, 204)

        other_ad = Ad.objects.create(
            author=self.user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='Private ad',
            description='No access',
            price='900.00',
            condition=Ad.CONDITION_NEW,
            status=Ad.STATUS_ACTIVE,
        )

        self.client.force_authenticate(user=self.other_user)
        patch_response = self.client.patch(
            reverse('ad-detail', args=[other_ad.id]),
            {'title': 'Hacked title'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, 403)

        delete_response = self.client.delete(reverse('ad-detail', args=[other_ad.id]))
        self.assertEqual(delete_response.status_code, 403)

    def test_can_upload_photo_to_guest_ad(self):
        guest_user, _ = User.objects.get_or_create(
            username='guest',
            defaults={'email': 'guest@local.invalid', 'is_active': True},
        )
        ad = Ad.objects.create(
            author=guest_user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='Car with photo',
            description='Nice car',
            price='5000.00',
            condition=Ad.CONDITION_NEW,
            status=Ad.STATUS_ACTIVE,
        )

        image = io.BytesIO()
        Image.new('RGB', (100, 100), color='blue').save(image, format='JPEG')
        image.seek(0)

        response = self.client.post(
            reverse('ad-images', args=[ad.id]),
            {'image': SimpleUploadedFile('car.jpg', image.read(), content_type='image/jpeg'), 'is_main': 'true'},
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ad.images.count(), 1)
        self.assertTrue(ad.images.filter(is_main=True).exists())

    def test_max_five_images_and_single_main_image(self):
        ad = Ad.objects.create(
            author=self.user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='Car with photo',
            description='Nice car',
            price='5000.00',
            condition=Ad.CONDITION_NEW,
            status=Ad.STATUS_ACTIVE,
        )

        self.client.force_authenticate(user=self.user)
        for index in range(5):
            image = io.BytesIO()
            Image.new('RGB', (100, 100), color=index).save(image, format='JPEG')
            image.seek(0)
            response = self.client.post(
                reverse('ad-images', args=[ad.id]),
                {'image': SimpleUploadedFile(f'car{index}.jpg', image.read(), content_type='image/jpeg')},
                format='multipart',
            )
            self.assertEqual(response.status_code, 201)

        image = io.BytesIO()
        Image.new('RGB', (100, 100), color='red').save(image, format='JPEG')
        image.seek(0)
        response = self.client.post(
            reverse('ad-images', args=[ad.id]),
            {'image': SimpleUploadedFile('car6.jpg', image.read(), content_type='image/jpeg')},
            format='multipart',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(ad.images.count(), 5)
        self.assertEqual(ad.images.filter(is_main=True).count(), 1)


class AdFilterSearchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller2', email='seller2@example.com', password='StrongPass123!')
        self.city = City.objects.create(name='Ош')
        self.district = District.objects.create(name='Район А', city=self.city)
        self.category = Category.objects.create(name='Электроника')
        self.ad = Ad.objects.create(
            author=self.user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='iPhone 15',
            description='Fast mobile phone',
            price='50000.00',
            condition=Ad.CONDITION_NEW,
            status=Ad.STATUS_ACTIVE,
        )

    def test_search_and_filters_work(self):
        response = self.client.get(
            reverse('ads-list'),
            {
                'search': 'iphone',
                'min_price': '30000',
                'max_price': '60000',
                'category': self.category.id,
                'city': self.city.id,
                'district': self.district.id,
                'condition': Ad.CONDITION_NEW,
                'ordering': 'cheapest',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'iPhone 15')
