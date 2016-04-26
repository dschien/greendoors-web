from django.contrib.auth.models import User

__author__ = 'schien'

import time

from api.models import House, Note

from rest_framework.test import APITestCase

from TestMixins import OAuthTestCaseMixin


class DeleteHouseTests(OAuthTestCaseMixin, APITestCase):
    """
        API for submitting Notes
    """
    fixtures = ['test_data.json']

    def test_delete_house_with_note(self):
        user1 = User.objects.all()[0]
        house1 = House.objects.all()[0]
        note = Note(text="Test", user=user1, timestamp=time.time(), house=house1)
        note.save()
        self.assertTrue(len(Note.objects.all()) == 1)
        house1.delete()

        self.assertTrue(len(Note.objects.all()) == 1)
        self.assertTrue(Note.objects.all()[0].text == "Test")



