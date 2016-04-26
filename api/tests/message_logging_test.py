from rest_framework.test import APITestCase

from api.models import LoggerMessage
from api.tests.TestMixins import OAuthTestCaseMixin


__author__ = 'schien'

from django.core.urlresolvers import reverse


class MessageLoggingTest(OAuthTestCaseMixin, APITestCase):
    """
    API functions for app login
    """
    fixtures = ['test_data.json']


    def test_anon_logging(self):
        self.assertTrue(LoggerMessage.objects.count() == 0)

        data = {'message': 'Some message'}
        response = self.client.post(reverse('app_log_message'), data)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.content == "1")

        self.assertTrue(LoggerMessage.objects.count() == 1)
        self.assertTrue(LoggerMessage.objects.all()[0].message == "Some message")
        self.assertTrue(LoggerMessage.objects.all()[0].user is None)


    def test_mapping_before_month(self):
        user = self.setCredentialsForAnyUser()
        data = {'message': 'old'}
        response = self.client.post(reverse('app_log_message'), data)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.content == "1")

        self.assertTrue(LoggerMessage.objects.count() == 1)
        self.assertTrue(LoggerMessage.objects.all()[0].message == "old")
        self.assertTrue(LoggerMessage.objects.all()[0].user is not None)

        self.assertTrue(user.log_messages.all()[0].message == "old")

