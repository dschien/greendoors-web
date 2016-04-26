import json
import re
import datetime
from rest_framework.test import APITestCase

from api.management.commands.import_exceldata import version_regexp
from api.models import App

__author__ = 'schien'

from django.core.urlresolvers import reverse


class DataUpdateTest(APITestCase):
    """
    API functions for app login
    """
    fixtures = ['test_data.json']

    def assertData(self, response):
        self.assertTrue(response.status_code == 200)
        self.assertTrue('houses' in response.data)
        self.assertTrue('image' in response.data['houses'][0])

        self.assertTrue(len(response.data['houses'][0]['image']) > 1000)
        self.assertTrue('measures' in response.data['houses'][0])
        print response.data['houses'][0]


    def test_authenticated_update(self):
        """
        Check simple register successful
        """
        c = self.client
        token = 'c01d6ce7483e183de08346eb608e6c77fa8d7dd5'

        data = {'version': 'old'}
        c.credentials(HTTP_AUTHORIZATION=('Bearer %s' % token))
        url = reverse('api_update')
        response = c.post(url, data, format='json')

        self.assertData(response)

    def test_anon_update(self):
        data = {'version': 'old'}
        response = self.client.post(reverse('api_update'), data)

        self.assertData(response)

    def test_mapping_before_month(self):
        """
        Tests that all houses which should only be on the map during a month after the openday are
        passed to clients.
        """
        app = App.objects.all()[0]
        app.openday = datetime.date.today() - datetime.timedelta(days=15)
        app.save()

        data = {'version': 'old'}
        response = self.client.post(reverse('api_update'), data)

        houses = response.data['houses']

        ids = []
        for house in houses:
            ids.append(house['id'])
        self.assertTrue(21 in ids)

    def test_mapping_after_month(self):
        """
        Tests that houses which should not be on the map after a month after the openday are
        not passed to clients.
        """
        app = App.objects.all()[0]
        app.openday = datetime.date.today() - datetime.timedelta(days=30)
        app.save()

        data = {'version': 'old'}
        response = self.client.post(reverse('api_update'), data)

        houses = response.data['houses']
        for house in houses:
            self.assertTrue(house['id'] != 21)


    def test_no_update(self):
        current_version = App.objects.all()[0].model_version
        data = {'version': current_version}

        response = self.client.post(reverse('api_update'), data)
        self.assertTrue(response.status_code == 204)

    def test_version_regexp(self):
        name = 'Template_v2.3.xlsx'

        matches = re.findall(version_regexp, name)
        # matches = re.findall(r'(\d+.\d+)', name)
        print matches
        self.assertTrue(matches[0][0] == '2.3')