from bs4 import BeautifulSoup
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from api.models import House

__author__ = 'schien'
from django.test import TestCase, Client


class BasicTest(TestCase):
    fixtures = ['test_data.json']

    def test_simple_response(self):
        c = Client()
        response = c.get('/web/')

        self.assertTrue(response.content.startswith('Hello World'))


class LoginTest(TestCase):
    fixtures = ['test_data.json']
    def test_test_login(self):
        self.user = User.objects.create(username='testuser', password='12345', is_active=True, is_staff=True,
                                        is_superuser=True)

        self.user.set_password('hello')
        self.user.save()
        user = authenticate(username='testuser', password='hello')

        c = Client()
        login = c.login(username='testuser', password='hello')
        self.assertTrue(login)

    def test_test_get_index(self):
        c = Client()
        # c.login(username='tester', password='test')
        response = c.get('/web/')
        print response.content
        soup = BeautifulSoup(response.content)
        self.assertEqual(soup.string, "Hello World")


def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class ImageTest(TestCase):
    fixtures = ['test_data.json']

    def test_get_image(self):

        # c.login(username='tester', password='test')
        response = self.client.get(reverse('web:detail', kwargs={'pk': 1}))

        print response.content
        soup = BeautifulSoup(response.content)
        self.assertEqual(soup.string, "Hello World")