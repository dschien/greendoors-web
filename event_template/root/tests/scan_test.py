import json

__author__ = 'schien'

from rest_framework import status
from api.tests.TestMixins import OAuthTestCaseMixin

from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from <%= name %>.models import Scan


class ScanAPITests(OAuthTestCaseMixin, APITestCase):
    """
    API for submitting scans
    """
    fixtures = ['backend_test_data.json']


    def get_scans(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.scans.all()) == 0)
        scan = Scan(user=user, text="0001")
        scan.save()

        response = self.client.get(reverse('scan-list'))

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(json.loads(response.content)[0]['text'] == "0001")

    def set_scan(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.scans.all()) == 0)

        data = {"text": "0001"}
        response = self.client.post(reverse('scan-list'), data, format='json')
        print response

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.scans.all()) == 1)
        self.assertTrue(user.scans.all()[0].text == "0001")


    def test_duplicates(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.scans.all()) == 0)
        scan = Scan(user=user, text="0001")
        scan.save()

        data = {"text": "0001"}
        response = self.client.post(reverse('scan-list'), data, format='json')
        print response

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.scans.all()) == 1)
        self.assertTrue(user.scans.all()[0].text == "0001")

