from django.urls import reverse
from rest_framework.test import APITestCase

from apps.locations.models import City, District


class LocationApiTests(APITestCase):
    def test_city_and_district_list(self):
        city = City.objects.create(name='Ош')
        District.objects.create(name='Район А', city=city)

        response = self.client.get(reverse('cities'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        district_response = self.client.get(reverse('districts'), {'city': city.id})
        self.assertEqual(district_response.status_code, 200)
        self.assertEqual(len(district_response.data), 1)

    def test_district_must_belong_to_selected_city(self):
        city_1 = City.objects.create(name='Ош')
        city_2 = City.objects.create(name='Бишкек')
        district_2 = District.objects.create(name='Район Б', city=city_2)

        response = self.client.patch(
            '/api/profile/',
            {'city': city_1.id, 'district': district_2.id},
            format='json',
        )

        self.assertEqual(response.status_code, 401)
