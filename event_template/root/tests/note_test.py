import json

from <%= name %>.views import NoteView


__author__ = 'schien'

from rest_framework import status
from api.tests.TestMixins import OAuthTestCaseMixin

from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.core.urlresolvers import reverse

from <%= name %>.models import House, Note


class NoteAPITests(OAuthTestCaseMixin, APITestCase):
    """
    API for submitting notes
    """
    fixtures = ['backend_test_data.json']


    def get_notes(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.notes.all()) == 0)
        house = House.objects.all()[0]
        note = Note(user=user, text="0001", house=house)
        note.save()

        response = self.client.get(reverse('note-list'))

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(json.loads(response.content)[0]['text'] == "0001")

    def set_note(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.notes.all()) == 0)
        house = House.objects.all()[0]
        data = {"text": "0001", 'house': house.pk}
        response = self.client.post(reverse('note-list'), data, format='json')
        print response

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.notes.all()) == 1)
        self.assertTrue(user.notes.all()[0].text == "0001")


    def test_duplicates(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.notes.all()) == 0)
        house = House.objects.all()[0]
        note = Note(user=user, text="0001", house=house)
        note.save()

        data = {"text": "0001", 'house': house.pk}
        response = self.client.post(reverse('note-list'), data, format='json')
        print response

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.notes.all()) == 1)
        self.assertTrue(user.notes.all()[0].text == "0001")

    def requestNote(self, user, note):
        factory = APIRequestFactory()
        request = factory.get(reverse('note-detail', args=[note]))
        force_authenticate(request, user=user)
        view = NoteView.as_view()
        response = view(request)
        response.render()
        return response

    def test_get_note(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.notes.all()) == 0)

        house = House.objects.all()[0]
        note = Note(user=user, text="0001", house=house)
        note.save()
        response = self.requestNote(user, note.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)[0]['text'] == "0001")
        self.assertTrue(len(user.notes.all()) == 1)