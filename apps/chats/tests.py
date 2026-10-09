from django.urls import reverse
from rest_framework.test import APITestCase

from apps.ads.models import Ad, Category
from apps.locations.models import City, District
from apps.users.models import User


class ChatApiTests(APITestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(username='buyer', email='buyer@example.com', password='StrongPass123!')
        self.seller = User.objects.create_user(username='seller', email='seller@example.com', password='StrongPass123!')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='StrongPass123!')
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

    def test_create_conversation_and_send_message(self):
        self.client.force_authenticate(user=self.buyer)
        create_response = self.client.post(reverse('conversations-list'), {'ad': self.ad.id}, format='json')
        self.assertEqual(create_response.status_code, 201)

        conversation_id = create_response.data['id']
        message_response = self.client.post(
            reverse('conversation-messages', args=[conversation_id]),
            {'text': 'Hello, is it available?'},
            format='json',
        )
        self.assertEqual(message_response.status_code, 201)

        get_response = self.client.get(reverse('conversation-messages', args=[conversation_id]))
        self.assertEqual(get_response.status_code, 200)
        self.assertGreater(len(get_response.data), 0)

    def test_cannot_create_conversation_with_own_ad_or_see_foreign_chat(self):
        self.client.force_authenticate(user=self.seller)
        own_response = self.client.post(reverse('conversations-list'), {'ad': self.ad.id}, format='json')
        self.assertEqual(own_response.status_code, 403)

        self.client.force_authenticate(user=self.buyer)
        conversation = self.client.post(reverse('conversations-list'), {'ad': self.ad.id}, format='json')
        conversation_id = conversation.data['id']

        self.client.force_authenticate(user=self.other_user)
        list_response = self.client.get(reverse('conversations-list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 0)

        message_response = self.client.get(reverse('conversation-messages', args=[conversation_id]))
        self.assertEqual(message_response.status_code, 403)
