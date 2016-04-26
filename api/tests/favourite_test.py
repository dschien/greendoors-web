import time
from rest_framework import status

__author__ = 'schien'

from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from api.models import House, Favourite
from api.tests.constants import house_serializer_id_field
from TestMixins import OAuthTestCaseMixin


class FavouriteAPITests(OAuthTestCaseMixin, APITestCase):
    """
    API for submitting scans
    """
    fixtures = ['test_data.json']

    def test_bulk_fav(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_favourite')
        house = House.objects.all()[0]
        self.assertTrue(house)
        self.assertTrue(len(user.favourites.all()) == 0)
        data = [{house_serializer_id_field: house.pk, 'timestamp': time.time(), 'fav': "True"}]
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.favourites.all()) == 1)
        self.assertTrue(user.favourites.all()[0].house == house)

    def test_remove_fav(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_favourite')
        house = House.objects.all()[0]
        self.assertTrue(house)

        data = [{house_serializer_id_field: house.pk, 'timestamp': time.time(), 'fav': "True"}]
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.favourites.all()) == 1)
        self.assertTrue(user.favourites.all()[0].house == house)

        data = [{house_serializer_id_field: house.pk, 'timestamp': time.time(), 'fav': "False"}]
        response = self.client.post(url, data, format='json')
        # print response.status_code
        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.favourites.all()) == 0)

    def test_update_fav(self):
        # if a fav already exists, then sending it again will not do anything
        user = self.setCredentialsForAnyUser()
        url = reverse('app_favourite')
        house = House.objects.all()[0]

        data = [{house_serializer_id_field: house.pk, 'timestamp': time.time(), 'fav': "True"}]
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.favourites.all()) == 1)
        self.assertTrue(user.favourites.all()[0].house == house)

        data = [{house_serializer_id_field: house.pk, 'timestamp': time.time(), 'fav': "True"}]
        response = self.client.post(url, data, format='json')
        self.assertTrue(len(user.favourites.all()) == 1)

        favs = Favourite.objects.filter(house=house.pk, user=user.pk)
        self.assertTrue(len(favs) == 1)

