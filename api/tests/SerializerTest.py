from django.contrib.auth.models import User
from django.test import TestCase
from api.models import House

from api.serializers import NoteSerializer, FavouriteSerializer
from api.tests.constants import house_serializer_id_field

__author__ = 'schien'


class SerializerTest(TestCase):
    fixtures = ['test_data.json']

    # def test_house_serializer(self):
    #     house = House.objects.all()[0]
    #     serializer = HouseSerializer(data={house_serializer_id_field: house.pk})
    #     print serializer.errors
    #     self.assertTrue(serializer.is_valid())
    #     self.assertTrue(serializer.object.pk == 1)
    #     self.assertTrue(serializer.object.pk == house.pk)
    #     self.assertTrue(serializer.object.address == house.address)
    #
    # def test_user_serializer(self):
    #     user = User.objects.all()[0]
    #     serializer = UserSerializer(data={'user': user.pk})
    #     print serializer.errors
    #     self.assertTrue(serializer.is_valid())
    #     self.assertTrue(serializer.object.pk == user.pk)
    #     self.assertTrue(serializer.object.username == user.username)

    def test_note_serializer(self):
        house = House.objects.all()[0]
        user = User.objects.all()[0]
        serializer = NoteSerializer(
            data={house_serializer_id_field: house.pk, 'text': 'Test Text', 'timestamp': 1378073890220,
                  'user': user.pk})
        print serializer.errors
        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.object.user.pk == user.pk)
        self.assertTrue(serializer.object.house.pk == 1)

    def test_fav_serializer(self):
        house = House.objects.all()[0]
        user = User.objects.all()[0]
        serializer = FavouriteSerializer(
            data={house_serializer_id_field: house.pk, 'timestamp': 1378073890220,
                  'user': user.pk})
        print serializer.errors
        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.object.user.pk == user.pk)
        self.assertTrue(serializer.object.house.pk == 1)

