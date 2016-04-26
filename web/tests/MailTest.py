__author__ = 'schien'
from bs4 import BeautifulSoup
from django.core.urlresolvers import reverse
from api.models import Message

__author__ = 'schien'
from django.test import TestCase


class ImageTest(TestCase):
    fixtures = ['web_test_data.json']


    def test_get_image(self):
        key = Message.objects.all()[0].key

        # c.login(username='tester', password='test')

        response = self.client.post(reverse('web:contact', {'text': 'answer'}, kwargs={'key': key}))

        print response.content
        soup = BeautifulSoup(response.content)
        self.assertEqual(soup.string, "Hello World")