import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

import api
# from api.views import register_by_access_token


__author__ = 'schien'

from django.core.urlresolvers import reverse


class LoginTest(TestCase):
    """
    API functions for app login
    """
    fixtures = ['test_data.json']

    # todo implement unsuccessful scenarios, i.e. prevent unauthorised access

    uuid = '49b44243-a240-49bb-8076-1dee1782e1fa'
    device = {'uuid': uuid, 'cordova': 'test', 'platform': 'local', 'version': '1', 'model': '1F'}

    def requestRegistration(self, data, viewname='app_register'):
        factory = APIRequestFactory()
        request = factory.post(reverse(viewname), data, format='json')
        view = api.views.RegisterView.as_view()
        response = view(request)
        return response

    def test_oauth_access_token(self):
        """
        Check simple register successful - first register to get the plain text password
        """
        users = User.objects.filter(username='test')
        self.assertTrue(len(users) == 0)

        password = "123test"
        username = "test3"
        data = {'username': username, 'password': password, 'email': 'test@me.com',
                'newsletter': 'false', 'research': 'true', 'device': self.device}

        response = self.requestRegistration(data)

        self.assertTrue('client_id' in response.data)
        self.assertTrue(not 'password' in response.data)

        data = {'client_id': response.data['client_id'],
                'client_secret': response.data['client_secret'],
                'username': username, 'password': password,
                'grant_type': 'password'}

        response = self.client.post(reverse('oauth2:access_token'), data=data)

        self.assertTrue(json.loads(response.content))
        self.assertTrue(response.status_code == 200)

        # disabled because login is handled by oauth provider

    def test_fb_oauth_test(self):
        key = ''

        # factory = APIRequestFactory()
        response = self.client.post(reverse('register_by_token', kwargs={'backend': 'facebook'}), {'access_token': key},
                               format='json')
        print response
