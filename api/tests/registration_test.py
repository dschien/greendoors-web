from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
import api
from api.models import Device


__author__ = 'schien'
from rest_framework.test import APIRequestFactory
from django.core.urlresolvers import reverse


class RegistrationTest(APITestCase):
    """
    API functions for app login
    """
    fixtures = ['test_data.json']

    uuid = '49b44243-a240-49bb-8076-1dee1782e1fa'
    device = {'uuid': uuid, 'cordova': 'test', 'platform': 'local', 'version': '1', 'model': '1F'}

    def requestRegistration(self, data, viewname='app_register'):
        factory = APIRequestFactory()
        request = factory.post(reverse(viewname), data, format='json')
        view = api.views.RegisterView.as_view()
        response = view(request)
        return response

    def test_register(self):
        """
        Check simple register successful
        """
        users = User.objects.filter(username='test')
        self.assertTrue(len(users) == 0)

        username = "test3"
        data = {'username': username, 'password': "123test", 'email': 'test@me.com',
                'newsletter': 'false', 'research': 'true', 'device': self.device}

        response = self.requestRegistration(data)

        self.assertTrue('client_id' in response.data)
        self.assertTrue(not 'password' in response.data)

        users = User.objects.filter(username=username)
        self.assertTrue(len(users) == 1)
        user = users[0]
        profile = user.user_profile
        self.assertTrue(profile.research)
        self.assertFalse(profile.newsletter)

        phone = Device.objects.get(user=user)

        self.assertTrue(phone.uuid == self.uuid)
        self.assertTrue(phone.cordova == self.device['cordova'])


    def test_register_existing(self):
        """
        Check simple register successful
        """

        data = {'username': User.objects.all()[0].username, 'password': "123test", 'email': 'dschien@gmail.com',
                'device': self.device, 'newsletter': 'true', 'research': 'true'}

        response = self.requestRegistration(data)
        self.assertTrue(response.status_code == status.HTTP_400_BAD_REQUEST)
        self.assertTrue(not 'client_id' in response.data)
        self.assertTrue('User with this Username already exists.' in response.data['username'])

    def test_error_missing_uuid(self):
        data = {'username': "test", 'password': "123test", 'email': 'test@me.com',
                'newsletter': 'true', 'device': self.device}

        response = self.requestRegistration(data)
        self.assertTrue(response.status_code == status.HTTP_400_BAD_REQUEST)
        self.assertTrue(not 'client_id' in response.data)

    def test_error_missing_flag(self):
        data = {'username': "test2", 'password': "123test", 'email': 'test@me.com',
                'newsletter': "True", 'device': self.device}

        response = self.requestRegistration(data)
        self.assertTrue(response.status_code == status.HTTP_400_BAD_REQUEST)
        self.assertTrue('research' in response.data)
        self.assertTrue(not 'client_id' in response.data)

    def test_device_optional(self):
        username = "test_dev_opt"
        data = {'username': username, 'password': "123test", 'email': 'test@me.com',
                'newsletter': "True", 'research': "True"}

        response = self.requestRegistration(data)

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue('client_id' in response.data)

        users = User.objects.filter(username=username)
        self.assertTrue(len(users) == 1)
        user = users[0]

        phone = Device.objects.get(user=user)

        self.assertTrue(phone is not None)

    def test_register_uuid_only(self):
        """
        Legacy use case for first app store version
        """
        username = "testuuid"
        data = {'username': username, 'password': "123test", 'email': 'test@me.com',
                'newsletter': "True", 'research': "True", 'uuid': '49b44243-a240-49bb-8076-1dee1782e1fa'}

        response = self.requestRegistration(data, viewname='v1_api_register')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue('client_id' in response.data)

        users = User.objects.filter(username=username)
        self.assertTrue(len(users) == 1)
        user = users[0]
        profile = user.user_profile
        phone = Device.objects.get(user=user)

        self.assertTrue(phone.uuid == self.uuid)

# todo test that no other phones can be created?
class PhoneAPITests(APITestCase):
    """
        API for submitting Notes

    """
    fixtures = ['test_data.json']

    def test_post_note(self):
        c = self.client
        c.credentials(HTTP_AUTHORIZATION='Bearer 3d827895642197e089484a56ea021e97df402a9a')
        url = reverse('app_phone')
        data = {'uuid': '49b44243-a240-49bb-8076-1dee1782e1fe'}
        response = c.post(url, data, format='json')
        self.assertTrue('created' in response.data)



