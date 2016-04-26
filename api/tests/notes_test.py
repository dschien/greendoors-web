import json
import time

from rest_framework import status

import api
from api.models import House, Note


__author__ = 'schien'

from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.core.urlresolvers import reverse

from api.tests.constants import house_serializer_id_field
from TestMixins import OAuthTestCaseMixin


class NotesAPITests(OAuthTestCaseMixin, APITestCase):
    """
        API for submitting Notes
    """
    fixtures = ['test_data.json']

    def test_bulk_notes(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_note')

        timestamp = 1378073890220
        data = [{house_serializer_id_field: 1, 'text': 'Test Text', 'timestamp': timestamp},
                {house_serializer_id_field: 3, 'text': 'Test Text 3', 'timestamp': timestamp + 1}]
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.notes.all()) == 2)

    def test_no_duplicate_bulk_notes(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_note')

        timestamp = 1378073890220
        data = [{house_serializer_id_field: 1, 'text': 'Test Text', 'timestamp': timestamp},
                {house_serializer_id_field: 1, 'text': 'Test Text', 'timestamp': timestamp}]
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.notes.all()) == 1)

    def test_update_note(self):
        user = self.setCredentialsForAnyUser()
        url = reverse('app_note')

        house_1_id = 1
        house_3_id = 3
        timestamp = 1378073890220
        data = [{house_serializer_id_field: house_1_id, 'text': 'Test Text', 'timestamp': timestamp},
                {house_serializer_id_field: house_3_id, 'text': 'Test Text 3', 'timestamp': timestamp + 1}]
        response = self.client.post(url, data, format='json')

        self.assertTrue(len(user.notes.all()) == 2)

        house_1_updated_text = 'Updated text'
        house_3_updated_text = 'update 2'
        data = [{house_serializer_id_field: house_1_id, 'text': house_1_updated_text, 'timestamp': timestamp + 2},
                {house_serializer_id_field: house_3_id, 'text': house_3_updated_text, 'timestamp': timestamp + 3}]
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.notes.all()) == 2)
        self.assertTrue(House.objects.get(pk=house_1_id).note.all()[0].text == house_1_updated_text)


    def getNote(self, user, scan):
        factory = APIRequestFactory()
        request = factory.get(reverse('note_detail', args=[scan]))
        force_authenticate(request, user=user)
        view = api.views.BulkNoteList.as_view()
        response = view(request)
        response.render()
        return response

    def createNote(self, user, text, house=None):
        note = Note(text=text, user=user, timestamp=time.time(), house=house)
        note.save()

        return note

    def test_get_note(self):
        user = self.setCredentialsForAnyUser()
        self.assertTrue(len(user.notes.all()) == 0)
        noteText = "0001"
        house = House.objects.all()[0]
        note = self.createNote(user, noteText, house)
        response = self.getNote(user, note.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)[0]['text'] == noteText)
        self.assertTrue(len(user.notes.all()) == 1)