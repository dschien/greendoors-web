from rest_framework.fields import BooleanField, EmailField

__author__ = 'schien'
from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Scan, Note, Device, Message, UserProfile, Favourite, House, InstalledMeasure


class UserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def restore_object(self, attrs, instance=None):
        if instance:  # Update
            user = instance
            user.username = attrs['username']
            user.email = attrs['email']
        else:
            user = User(username=attrs['username'], email=attrs['email'],
                        is_staff=False, is_active=True, is_superuser=False)
        user.set_password(attrs['password'])
        # remove password field
        del self.fields['password']
        # note I don't save() here. The view's create() does that.
        return user


class RegistrationSerializer(serializers.ModelSerializer):
    email = EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def restore_object(self, attrs, instance=None):
        # create user
        if instance:  #Update
            user = instance
            user.username = attrs['username']
            user.email = attrs['email']
        else:
            user = User(username=attrs['username'], email=attrs['email'],
                        is_staff=False, is_active=True, is_superuser=False)
        user.set_password(attrs['password'])
        # remove password field
        del self.fields['password']
        # note I don't save() here. The view's create() does that.

        return user

# create user profile


class NonDefaultBooleanField(BooleanField):
    default = None


class UserProfileSerializer(serializers.ModelSerializer):
    research = NonDefaultBooleanField(source='research')
    newsletter = NonDefaultBooleanField(source='newsletter')

    class Meta:
        model = UserProfile
        fields = ('research', 'newsletter')


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['uuid', 'model', '']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['uuid', 'model', 'cordova', 'platform', 'version']


class HomeOwnerProfileSerializer(serializers.ModelSerializer):
    pass


class ScanSerializer(serializers.ModelSerializer):
    # user = serializers.Field(source='user.username')
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Scan
        fields = ('text', 'created', 'user', 'timestamp')


class FavouriteSerializer(serializers.ModelSerializer):
    house = serializers.PrimaryKeyRelatedField(queryset=House.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favourite
        fields = ('timestamp', 'user', 'house')


class MessageSerializer(serializers.ModelSerializer):

    # we set
    class Meta:
        model = Message
        fields = ('text', )


class HouseSerializer(serializers.ModelSerializer):
    # house = serializers.IntegerField(source='pk')

    class Meta:
        model = House
        # fields = ('house',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class NoteSerializer(serializers.ModelSerializer):
    house = serializers.PrimaryKeyRelatedField(queryset=House.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Note
        fields = ('text', 'created', 'timestamp', 'user', 'house')
        # depth = 1


# class ImageSerializer(serializers.ModelSerializer):
#     image = serializers.CharField()
#
#     class Meta:
#         model = HouseImage
#         # fields = ('image',)
#
#     def get_related_field(self, model_field, related_model, to_many):
#         return self.image


class InstalledMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstalledMeasure


class ClientDataSerializer(serializers.ModelSerializer):
    # image = ImageSerializer()
    measures = InstalledMeasureSerializer()

    class Meta:
        model = House
        # depth =