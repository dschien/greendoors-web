from rest_framework import status
from api.models import TrackableURL, RedirectUrl

__author__ = 'schien'

from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from TestMixins import OAuthTestCaseMixin


class RedirectLinkAPITests(OAuthTestCaseMixin, APITestCase):
    """
    API for submitting scans
    """
    fixtures = ['test_data.json']

    def test_create_link(self):
        user = self.setCredentialsForAnyUser()
        view_url = reverse('api_generate_url')
        target_url = 'http://www.google.de'
        data = {'url': target_url, 'username': user.username}

        objects_all = TrackableURL.objects.all()
        size_before = len(objects_all)
        response = self.client.post(view_url, data, format='json')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)

        objects_all = TrackableURL.objects.all()
        size_after = len(objects_all)

        self.assertTrue(size_before + 1 == size_after)

        url_filter = RedirectUrl.objects.filter(user=user)
        self.assertTrue(url_filter[0].target_url.url == target_url)