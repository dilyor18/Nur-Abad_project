from django.urls import reverse
from rest_framework.test import APITestCase

from apps.locations.models import City, District
from apps.news.models import News, NewsCategory
from apps.users.models import User


class NewsApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='author', email='author@example.com', password='StrongPass123!')
        self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='StrongPass123!')
        self.city = City.objects.create(name='Ош')
        self.district = District.objects.create(name='Центр', city=self.city)
        self.category = NewsCategory.objects.create(name='Объявления')

    def test_create_news_starts_as_pending(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('news-list'),
            {
                'title': 'Новый проект',
                'slug': 'novyi-proekt',
                'content': 'Содержание новости',
                'category': self.category.id,
                'city': self.city.id,
                'district': self.district.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'PENDING')

    def test_news_feed_shows_only_published_and_filters_by_district(self):
        News.objects.create(
            author=self.user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='Published news',
            slug='published-news',
            content='Visible',
            status=News.STATUS_PUBLISHED,
        )
        News.objects.create(
            author=self.user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='Pending news',
            slug='pending-news',
            content='Hidden',
            status=News.STATUS_PENDING,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('news-list'), {'district': self.district.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Published news')

    def test_admin_can_publish_news(self):
        news = News.objects.create(
            author=self.user,
            category=self.category,
            city=self.city,
            district=self.district,
            title='To publish',
            slug='to-publish',
            content='Needs approval',
            status=News.STATUS_PENDING,
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse('news-moderate', args=[news.id]),
            {'status': News.STATUS_PUBLISHED},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], News.STATUS_PUBLISHED)
        news.refresh_from_db()
        self.assertEqual(news.status, News.STATUS_PUBLISHED)
