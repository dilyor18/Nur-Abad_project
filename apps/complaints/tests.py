from django.urls import reverse
from rest_framework.test import APITestCase

from apps.ads.models import Ad, Category
from apps.complaints.models import Report
from apps.locations.models import City, District
from apps.news.models import News, NewsCategory
from apps.users.models import User


class ComplaintApiTests(APITestCase):
    def setUp(self):
        self.reporter = User.objects.create_user(username='reporter', email='reporter@example.com', password='StrongPass123!')
        self.admin = User.objects.create_superuser(username='admin', email='admin2@example.com', password='StrongPass123!')
        self.city = City.objects.create(name='Ош')
        self.district = District.objects.create(name='Центр', city=self.city)
        self.category = Category.objects.create(name='Техника')
        self.news_cat = NewsCategory.objects.create(name='Новости')
        self.ad = Ad.objects.create(
            author=self.reporter,
            category=self.category,
            city=self.city,
            district=self.district,
            title='Сломанный девайс',
            description='Не работает',
            price='1000.00',
            condition=Ad.CONDITION_USED,
            status=Ad.STATUS_ACTIVE,
        )
        self.news = News.objects.create(
            author=self.reporter,
            category=self.news_cat,
            city=self.city,
            district=self.district,
            title='Плохая новость',
            slug='plohaya-novost',
            content='Текст',
            status=News.STATUS_PUBLISHED,
        )

    def test_user_can_create_reports_for_ad_news_and_user(self):
        self.client.force_authenticate(user=self.reporter)

        ad_response = self.client.post(
            reverse('reports-list'),
            {'target_type': Report.TARGET_AD, 'ad': self.ad.id, 'reason': 'Неправильный товар'},
            format='json',
        )
        self.assertEqual(ad_response.status_code, 201)

        news_response = self.client.post(
            reverse('reports-list'),
            {'target_type': Report.TARGET_NEWS, 'news': self.news.id, 'reason': 'Неправдоподобная информация'},
            format='json',
        )
        self.assertEqual(news_response.status_code, 201)

        user_response = self.client.post(
            reverse('reports-list'),
            {'target_type': Report.TARGET_USER, 'user': self.admin.id, 'reason': 'Спам'},
            format='json',
        )
        self.assertEqual(user_response.status_code, 201)

    def test_admin_can_list_and_update_report_status(self):
        report = Report.objects.create(
            reporter=self.reporter,
            target_type=Report.TARGET_AD,
            ad=self.ad,
            reason='Подозрительное объявление',
            status=Report.STATUS_PENDING,
        )

        self.client.force_authenticate(user=self.admin)
        list_response = self.client.get(reverse('reports-list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertGreaterEqual(len(list_response.data['results']), 1)

        update_response = self.client.patch(
            reverse('report-detail', args=[report.id]),
            {'status': Report.STATUS_RESOLVED, 'admin_note': 'Проверено'},
            format='json',
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['status'], Report.STATUS_RESOLVED)
