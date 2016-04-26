# Create your views here.
import logging
from smtplib import SMTPRecipientsRefused
import datetime

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import Http404
from provider.oauth2.models import Client
from rest_framework import mixins, status
from rest_framework.authentication import OAuth2Authentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from django.views.generic import RedirectView
from registration import signals

from api.models import Scan, Device, Note, House, Message, Favourite, App, RedirectUrl, Click, MessageThread, \
    TrackableURL, LoggerMessage
from api.serializers import ScanSerializer, NoteSerializer, DeviceSerializer, MessageSerializer, RegistrationSerializer, \
    UserProfileSerializer, FavouriteSerializer, ClientDataSerializer
from api.tests.constants import house_serializer_id_field
from api.view_mixins import LoggingMixin
from greendoors.services.mail_service import SMTPConnection
from web.views import insert_response_url_header


logger = logging.getLogger(__name__)


class RegisterView(LoggingMixin, APIView):
    """
    Full registration:
    - create user
    - create user profile
    - create phone
    """
    authentication_classes = []
    permission_classes = (AllowAny,)


    def post(self, request, format=None):
        userprofile_serializer = UserProfileSerializer(data=request.DATA)
        reg_serializer = RegistrationSerializer(data=request.DATA)
        if 'device' in request.DATA:
            phone_serializer = DeviceSerializer(data=request.DATA['device'])
        else:
            phone_serializer = DeviceSerializer(data=request.DATA)

        errors = {}
        if userprofile_serializer.is_valid() and reg_serializer.is_valid() and phone_serializer.is_valid():
            user = reg_serializer.save()
            data = reg_serializer.data

            phone = phone_serializer.object
            phone.user = user
            phone_serializer.save()
            data.update(phone_serializer.data)

            user_profile = userprofile_serializer.object
            user_profile.user = user
            userprofile_serializer.save()
            data.update(userprofile_serializer.data)

            # trigger user activation to send welcome email
            signals.user_activated.send(sender=self.__class__,
                                        user=user,
                                        request=request)

            # return the right client
            client = Client.objects.get(pk=1)

            data.update({'client_id': client.client_id, 'client_secret': client.client_secret})

            return Response(data, status=status.HTTP_201_CREATED)

        errors.update(reg_serializer.errors)
        errors.update(phone_serializer.errors)
        errors.update(userprofile_serializer.errors)

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class BulkScan(LoggingMixin, generics.ListCreateAPIView):
    """
    Provides get (list all) and post (single) for scans.
    """
    queryset = Scan.objects.all()
    serializer_class = ScanSerializer
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)

    # insert the user on save
    def pre_save(self, obj):
        obj.user = self.request.user

    def post(self, request, *args, **kwargs):
        errors = []
        result = []
        headers = {}

        data = request.DATA
        # array of msgs
        for msg_data in data:
            msg_data.update({'user': request.user.pk})
            serializer = ScanSerializer(data=msg_data)
            if serializer.is_valid():
                self.pre_save(serializer.object)
                try:
                    self.object = serializer.save(force_insert=True)
                except IntegrityError as e:
                    # catch duplicate errors - todo fix client, not to send duplicates...
                    continue

                result.append(serializer.data)
                headers.update(self.get_success_headers(serializer.data))
                continue
            if serializer.errors:
                errors.append(serializer.errors)

        if not errors:
            return Response(result, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class BulkHouseDataListCreateView(LoggingMixin, generics.ListCreateAPIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    def set_house_data(self, request, obj, house):
        obj.house = house

    # insert the user on save
    def pre_save(self, obj):
        obj.user = self.request.user

    def isDeleteInstance(self, data):
        return False

    def post(self, request, format=None):
        """
        Subverts a proper REST API by implementing create, update and delete logic.

        Acts on each element in the data array.

        Creation of new objects is the default. The serializer class is used to create a new model instance
         from each element's data.

        Update occurs if an element's data violates unique constraints. In this case, the attributes that cause the
         violation are used to find the model instance

        Deletion criteria are defined by subclasses in the method `isDeleteInstance`.
        """
        errors = []
        result = []
        headers = {}

        data = request.DATA
        # array of msgs
        for msg_data in data:
            msg_data.update({'user': request.user.pk})
            # default - create new
            serializer = self.get_serializer(data=msg_data)

            if not serializer.is_valid() and '__all__' in serializer.errors:
                # check if unique constraints apply to this data - then update
                meta_model = self.get_serializer_class().Meta.model
                kwargs = {}

                for property in meta_model._meta.unique_together[0]:
                    kwargs.update({
                        '{0}__{1}'.format(property, 'pk__exact'): msg_data[property],
                    })

                object = meta_model.objects.filter(**kwargs)[0]
                serializer = self.get_serializer(object, data=msg_data)

            if serializer.is_valid():
                if self.isDeleteInstance(msg_data):
                    if serializer.object.pk is not None:
                        # this should always be the case
                        serializer.object.delete()
                    else:
                        logger.warn(
                            'instance marked for deletion but wasn not found in db with these attributes {0}'.format(
                                msg_data))
                else:
                    self.pre_save(serializer.object)
                    obj = serializer.object
                    # the receiver is the home owner of this house
                    house = House.objects.get(pk=msg_data[house_serializer_id_field])
                    if house is None:
                        errors.append(
                            {house_serializer_id_field: 'not found'.format(msg_data[house_serializer_id_field])})
                        continue

                    self.set_house_data(self.request, obj, house)
                    try:
                        self.object = serializer.save()
                    except IntegrityError as e:
                        # catch duplicate errors - todo fix client, not to send duplicates...
                        continue
                    self.post_save(self.object, created=True)
                    result.append(serializer.data)
                    headers.update(self.get_success_headers(serializer.data))
                    continue
            if serializer.errors:
                errors.append(serializer.errors)

        if not errors:
            return Response(result, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class BulkFavList(BulkHouseDataListCreateView):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer

    def isDeleteInstance(self, data):
        if data['fav'] == 'False':
            return True
        return False


class BulkNoteList(BulkHouseDataListCreateView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class BulkMessageView(BulkHouseDataListCreateView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def pre_save(self, obj):
        """
        Starts a new thread with this message.
        """
        thread = MessageThread()
        thread.save()
        obj.thread = thread

        super(BulkMessageView, self).pre_save(obj)

    def post_save(self, message, created=False):
        # after object was saved, we have a key...
        # insert response header
        htmlify_text(message)
        message.text = insert_response_url_header(key=message.key, text=message.text)

        # send message
        logger.info('sending message {} from user {} to user {}'.format(message.pk, message.sender.pk,
                                                                        message.receiver.pk))
        try:

            house_id = message.receiver.home_owner_profile.house.all()[0].pk

            # todo factor out, reuse instance
            con = SMTPConnection()
            logger.debug("sending message:\n {0}".format(message.text))
            con.send_email(recipient_address=message.receiver.email,
                           subject="Greendoors Communications [House {0}]".format(house_id),
                           body=message.text)
            message.sent = True
            message.save()

        except SMTPRecipientsRefused as err:
            logger.error("Email sending refused for message {0}".format(message.pk))

    def set_house_data(self, request, obj, house):
        obj.sender = self.request.user
        obj.receiver = house.owner.user


def htmlify_text(message):
    unprocessed = message.text
    processed = re.sub(r'\r?\n', '<br>\n', unprocessed)
    message.text = processed


class PhoneCreate(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    Provides post (single) for phone.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def pre_save(self, obj):
        obj.user = self.request.user


class DataView(LoggingMixin, generics.GenericAPIView):
    """
    Send all data to client
    """

    # attemp oauth
    authentication_classes = [OAuth2Authentication]
    # even if not authenticated, allow the request
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        clientVersion = request.DATA['version']
        current_version = App.objects.all()[0].model_version
        if clientVersion == current_version:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # check date
            openday = App.objects.all()[0].openday
            now = datetime.date.today()

            houses = []
            for house in House.objects.all():
                # ignore houses that have opted out
                if house.mapping == House.MAPPING_MONTH and now - datetime.timedelta(days=29) > openday:
                    continue
                houses.append(house)

            houses_serializer = ClientDataSerializer(instance=houses, many=True)

            response = {'houses': houses_serializer.data, 'version': current_version}
            return Response(data=response, status=status.HTTP_200_OK)


class DeviceDataMixin(object):
    """
        Create a model instance.
        """

    def save_device_data(self, request, *args, **kwargs):
        phoneserializer = DeviceSerializer(data=request.DATA)

        if phoneserializer.is_valid():
            phoneserializer.object.user = request.user
            phoneserializer.save(force_insert=True)


class TrackingRedirectView(RedirectView):
    # def get(self, request, *args, **kwargs):
    # key = self.args[0]
    # # .. lookup target url for key from db
    #    target_url = 'http://www.google.de'
    #    return HttpResponseRedirect(target_url)

    def get_redirect_url(self, **kwargs):
        key = self.kwargs['key']

        # .. lookup target url for key from db
        manager = RedirectUrl.objects.filter(redirect_key__exact=key)

        if len(manager) == 1:
            redirect = manager[0]
            # add new click
            click = Click(redirect=redirect)
            # add the user agent
            if 'HTTP_USER_AGENT' in self.request.META:
                click.user_agent = self.request.META['HTTP_USER_AGENT'][:99]

            # set the user
            click.user = self.request.user
            click.redirect = redirect
            click.save()

            return redirect.target_url.url
        raise Http404


import json
from django.http import HttpResponse


class JSONResponse(HttpResponse):
    """
    Return a JSON serialized HTTP resonse
    """

    def __init__(self, request, data, status=200):
        serialized = json.dumps(data)
        super(JSONResponse, self).__init__(
            content=serialized,
            content_type='application/json',
            status=status)


class JSONViewMixin(object):
    """
    Add this mixin to a Django CBV subclass to easily return JSON data.
    """

    def json_response(self, data, status=status.HTTP_200_OK):
        return JSONResponse(self.request, data, status=status)


import re


def check_username(request):
    regex = r'^[\w.@+-]+$'
    if 'username' in request.GET:
        name = request.GET['username']
        if len(name) < 30 and re.match(regex, name) and not User.objects.filter(username__iexact=name):
            return HttpResponse({1})

    return HttpResponse(json.dumps({'message': 'Username Unavailable.'}), content_type="application/json")


@api_view(['POST'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((IsAdminUser,))
def create_url(request):
    if request.method == 'POST':
        username = request.DATA['username']
        url = request.DATA['url']

        t_url, created = TrackableURL.objects.get_or_create(url=url)
        t_url.save()

        # key = generate_url_key()
        user_filter = User.objects.filter(username=username)
        if len(user_filter) == 1:
            user = user_filter[0]
        else:
            raise Http404("username not found")

        redirect, created = RedirectUrl.objects.get_or_create(user=user, target_url=t_url)
        if created:
            redirect.save()

        domain = Site.objects.get(pk=1).domain

        result = "https://{0}{1}".format(domain, reverse('api_redirect', kwargs={'key': redirect.redirect_key}))
        return Response(result, status=status.HTTP_201_CREATED)


from social.apps.django_app.utils import strategy

# Define an URL entry to point to this view, call it passing the
# access_token parameter like ?access_token=<token>. The URL entry must
# contain the backend, like this:
#
# url(r'^register-by-token/(?P<backend>[^/]+)/$',
# 'register_by_access_token')

@strategy('social:complete')
@api_view(['POST'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((AllowAny,))
def register_by_access_token(request, backend):
    """
    For the respective backend and access token, register the user.
    If a user does not exist, it is created,
    From here, we can directly return our own access token.
    """
    # This view expects an access_token GET parameter
    token = request.DATA['access_token']
    backend = request.strategy.backend
    user = backend.do_auth(token)
    if user:
        from provider.oauth2.models import Client

        c = Client.objects.all()[0]
        from provider.oauth2.views import AccessTokenView

        access_token = AccessTokenView().get_access_token(None, user, 1, c)

        return HttpResponse(json.dumps({"access_token": access_token.token, "username": access_token.user.first_name}),
                            content_type="application/json",
                            status=status.HTTP_201_CREATED)
    else:
        return HttpResponse(json.dumps({'message': 'Login failed.'}), content_type="application/json",
                            status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((AllowAny,))
def log_message(request, ):
    batches = request.DATA['message']

    log = LoggerMessage(message=batches)

    if not request.user.is_anonymous():
        log.user = request.user

    log.save()

    return HttpResponse(json.dumps(1))

