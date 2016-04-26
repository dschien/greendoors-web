
import datetime


__author__ = 'schien'

from rest_framework import status
from api.tests.TestMixins import OAuthTestCaseMixin

from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse


class RoutingEventTests(OAuthTestCaseMixin, APITestCase):
    """
    API for submitting notes
    """
    fixtures = ['backend_test_data.json']

    def test_add_event(self):
        user = self.setCredentialsForAnyUser()

        data = {"route": "start", 'timestamp': datetime.datetime(1984, 7, 31, 4, 31)}
        response = self.client.post(reverse('user-action'), data, format='json')
        print response

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)
        self.assertTrue(len(user.<%= name %>_backbonerouteevent.all()) == 1)
        self.assertTrue(user.<%= name %>_backbonerouteevent.all()[0].route == "start")

    def test_anonym_add_event(self):
        data = {"route": "test", 'timestamp': datetime.datetime(2014, 7, 31, 4, 31)}
        response = self.client.post(reverse('user-action'), data, format='json')
        print response

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)

    #
    # def requestNote(self, user, note):
    #     factory = APIRequestFactory()
    #     request = factory.get(reverse('note-detail', args=[note]))
    #     force_authenticate(request, user=user)
    #     view = NoteView.as_view()
    #     response = view(request)
    #     response.render()
    #     return response
    #
    # def test_get_note(self):
    #     user = self.setCredentialsForAnyUser()
    #     self.assertTrue(len(user.notes.all()) == 0)
    #
    #     house = House.objects.all()[0]
    #     note = Note(user=user, text="0001", house=house)
    #     note.save()
    #     response = self.requestNote(user, note.pk)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(json.loads(response.content)[0]['text'] == "0001")
    #     self.assertTrue(len(user.notes.all()) == 1)