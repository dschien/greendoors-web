__author__ = 'schien'

from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from TestMixins import OAuthTestCaseMixin


class BulkAPITests(OAuthTestCaseMixin, APITestCase):
    """
    API for submitting scans
    """
    fixtures = ['test_data.json']

    def test_bulk_scan(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_bulk_scan')
        data = [{'text': '0001', 'timestamp': 1378073890220}, {'text': '0002', 'timestamp': 1378073890221}]
        response = self.client.post(url, data, format='json')
        # print "test result - response for post bulk scan upload: {0}".format(response.data)
        self.assertTrue(len(user.scans.all()) == 2)

    def test_bulk_with_single(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_bulk_scan')
        data = [{'text': '0001', 'timestamp': 1378073890220}]
        response = self.client.post(url, data, format='json')
        # print "test result - response for post bulk scan upload: {0}".format(response.data)
        self.assertTrue(len(user.scans.all()) == 1)


    def test_no_duplicate_scan(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_bulk_scan')
        data = [{'text': '0001', 'timestamp': 1378073890220}, {'text': '0001', 'timestamp': 1378073890220}]
        response = self.client.post(url, data, format='json')
        # print "test result - response for post bulk scan upload: {0}".format(response.data)
        self.assertTrue(len(user.scans.all()) == 1)
