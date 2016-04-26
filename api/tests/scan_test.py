__author__ = 'schien'
import json
import time

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

import api
from api.models import Scan
from TestMixins import OAuthTestCaseMixin


class ScanAPITests(OAuthTestCaseMixin, APITestCase):
    """
    API for submitting scans
    """
    fixtures = ['test_data.json']

    def requestScan(self, user, scan):
        factory = APIRequestFactory()
        request = factory.get(reverse('scan_detail', args=[scan]))
        force_authenticate(request, user=user)
        view = api.views.BulkScan.as_view()
        response = view(request)
        response.render()
        return response

    def createScan(self, user, text):
        scan = Scan(text=text, user=user, timestamp=time.time())
        scan.save()

        return scan

    def test_get_scan(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.scans.all()) == 0)
        scanText = "0001"
        scan = self.createScan(user, scanText)
        response = self.requestScan(user, scan.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)[0]['text'] == scanText)
        self.assertTrue(len(user.scans.all()) == 1)

