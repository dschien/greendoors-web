from provider.oauth2.models import AccessToken
from rest_framework.test import APITestCase
from api.models import House
from api.tests.constants import house_serializer_id_field

__author__ = 'schien'

from django.core.urlresolvers import reverse


class MessagesAPITests(APITestCase):
    """
        API for submitting Notes
    """
    fixtures = ['test_data.json']

    def test_post_message(self):
        c = self.client
        accesstoken = AccessToken.objects.all()[0]
        token = accesstoken.token
        user = accesstoken.user

        houseID = '1'
        data = [{house_serializer_id_field: houseID, 'text': 'This is a test.', 'timestamp': 1378073890220}]
        house = House.objects.get(pk=int(houseID))

        self.assertTrue(len(user.sent_messages.all()) == 0)
        rec_msg = house.owner.user.received_messages.all()
        self.assertTrue(len(rec_msg) == 0)

        c.credentials(HTTP_AUTHORIZATION=('Bearer %s' % token))
        url = reverse('app_message')
        response = c.post(url, data, format='json')

        print response.data
        self.assertTrue(response.status_code == 201)

        self.assertTrue(len(user.sent_messages.all()) == 1)
        rec_msg = house.owner.user.received_messages.all()
        self.assertTrue(len(rec_msg) == 1)

        # self.assertTrue('created' in response.data)

    def test_no_duplicate_msgs(self):
        c = self.client
        accesstoken = AccessToken.objects.all()[0]
        token = accesstoken.token
        user = accesstoken.user

        houseID = '1'
        data = [{house_serializer_id_field: houseID, 'text': 'This is a test.', 'timestamp': 1378073890220},
                {house_serializer_id_field: houseID, 'text': 'This is a test.', 'timestamp': 1378073890220}]
        house = House.objects.get(pk=int(houseID))

        prior_msgs = len(user.sent_messages.all())
        self.assertTrue(prior_msgs == 0)
        rec_msg = house.owner.user.received_messages.all()
        prior_rec_msgs = len(rec_msg)
        self.assertTrue(prior_rec_msgs == 0)

        c.credentials(HTTP_AUTHORIZATION=('Bearer %s' % token))
        url = reverse('app_message')
        response = c.post(url, data, format='json')

        print response.data
        self.assertTrue(response.status_code == 201)

        post_messages = len(user.sent_messages.all())
        self.assertTrue(post_messages == prior_msgs + 1)
        post_rec_msgs = len(house.owner.user.received_messages.all())
        self.assertTrue(post_rec_msgs == prior_rec_msgs + 1)



