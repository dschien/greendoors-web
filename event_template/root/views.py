import json
import logging
from smtplib import SMTPRecipientsRefused
import datetime
from django.utils import timezone

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import generics
from rest_framework.authentication import OAuth2Authentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import mixins, status

from api.models import Message, MessageThread
from api.serializers import MessageSerializer
from api.views import htmlify_text
# @TODO check project substitution
from <%= name %>.models import House, Favourite, Note, Scan, BackboneRouteEvent, App, Measure, MeasureCategory
from api.tests.constants import house_serializer_id_field
from greendoors.services.mail_service import SMTPConnection
from greendoors.services.report_service import ReportService
from web.views import insert_response_url_header


logger = logging.getLogger(__name__)

# from backend.models import Item
# @TODO check project substitution
from <%= name %>.serializers import HouseSerializer, MeasureSerializer, MeasureCategorySerializer, \
    FavouriteSerializer, NoteSerializer, \
    ScanSerializer, BackboneRouteEventSerializer


class HouseView(mixins.ListModelMixin, GenericAPIView):
    authentication_classes = [OAuth2Authentication]
    # even if not authenticated, allow the request
    permission_classes = (AllowAny,)
    model = House
    serializer_class = HouseSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class HouseDetail(mixins.RetrieveModelMixin, GenericAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    authentication_classes = [OAuth2Authentication]
    # even if not authenticated, allow the request
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class InstalledMeasureTypesQuerysetMixin(object):
    """
    Only show those measures from the set of all measure types known for which there is actually a installed measure present.
    """

    def get_queryset(self):

        wanted_items = set()
        for item in Measure.objects.all():

            for im in InstalledMeasure.objects.all():
                if im.measure.pk == item.pk:
                    wanted_items.add(item.pk)

        return Measure.objects.filter(pk__in=wanted_items)


class MeasureView(InstalledMeasureTypesQuerysetMixin, mixins.ListModelMixin, GenericAPIView):
    authentication_classes = [OAuth2Authentication]
    # even if not authenticated, allow the request
    permission_classes = (AllowAny,)
    # model = Measure
    serializer_class = MeasureSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MeasureDetail(mixins.RetrieveModelMixin, GenericAPIView):
    queryset = Measure.objects.all()
    serializer_class = MeasureSerializer
    authentication_classes = [OAuth2Authentication]
    # even if not authenticated, allow the request
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UserDataMixin(object):
    def get_queryset(self):
        queryset = super(UserDataMixin, self).get_queryset()
        return queryset.filter(user=self.request.user)


class IgnoreDuplicatesMixin(object):
    """
    Check if model already exists
    """

    def post(self, request, *args, **kwargs):
        data = request.DATA
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            model = self.get_serializer_class().Meta.model
            instances = model.objects.filter(user=self.request.user, house=data[house_serializer_id_field])
            if len(instances) > 0:
                # duplicate
                return Response(serializer.data, status=status.HTTP_201_CREATED,
                                headers=self.get_success_headers(serializer.data))

        return super(IgnoreDuplicatesMixin, self).create(request, *args, **kwargs)


class PreSaveUserMixin(object):
    def pre_save(self, obj):
        obj.user = self.request.user


class FavouriteView(PreSaveUserMixin, IgnoreDuplicatesMixin, UserDataMixin, generics.ListCreateAPIView):
    authentication_classes = [OAuth2Authentication]
    model = Favourite
    serializer_class = FavouriteSerializer


class ScanView(PreSaveUserMixin, UserDataMixin, generics.ListCreateAPIView):
    authentication_classes = [OAuth2Authentication]
    model = Scan
    serializer_class = ScanSerializer

    def post(self, request, *args, **kwargs):
        data = request.DATA
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            model = self.get_serializer_class().Meta.model
            instances = model.objects.filter(user=self.request.user, text=data['text'])
            if len(instances) > 0:
                # duplicate
                return Response(serializer.data, status=status.HTTP_201_CREATED,
                                headers=self.get_success_headers(serializer.data))

        return super(ScanView, self).create(request, *args, **kwargs)


class NoteView(PreSaveUserMixin, IgnoreDuplicatesMixin, UserDataMixin, generics.ListCreateAPIView):
    authentication_classes = [OAuth2Authentication]
    model = Note
    serializer_class = NoteSerializer


class FavouriteDetail(PreSaveUserMixin, UserDataMixin, generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    #lookup_field = 'house'


class NoteDetail(PreSaveUserMixin, UserDataMixin, generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    #lookup_field = 'house'


class InstalledMeasureCategoryQuerysetMixin(object):
    """
    Only show those measure categories for which there is actually a installed measure present.
    """

    def get_queryset(self):

        wanted_items = set()
        for item in MeasureCategory.objects.all():

            for im in InstalledMeasure.objects.all():
                if im.measure.category.pk == item.pk:
                    wanted_items.add(item.pk)

        return MeasureCategory.objects.filter(pk__in=wanted_items)


class MeasureCategoryView(InstalledMeasureCategoryQuerysetMixin, mixins.ListModelMixin, GenericAPIView):
    authentication_classes = (OAuth2Authentication,)
    # permission_classes = (IsAuthenticated,)
    # even if not authenticated, allow the request
    permission_classes = (AllowAny,)
    model = MeasureCategory
    serializer_class = MeasureCategorySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MeasureCategoryDetail(InstalledMeasureCategoryQuerysetMixin, mixins.RetrieveModelMixin, GenericAPIView):
    serializer_class = MeasureCategorySerializer
    authentication_classes = [OAuth2Authentication]
    # even if not authenticated, allow the request
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


def detail(request, scan):
    house = None

    house_objects_filter = House.objects.filter(pk=int(scan[0:4]))
    if house_objects_filter.exists():
        house = house_objects_filter[0]
    else:
        logger.info('Called code url with unknown code {0}'.format(scan))

    m = int(scan[5:8])
    measure = None
    if m > 0:
        measure_objects_filter = Measure.objects.filter(pk=m)
        if measure_objects_filter.exists():
            measure = measure_objects_filter[0]

    data = {'house': house, 'measurement': measure}
    # @TODO check project substitution
    return render(request, '<%= name %>/barcode.html', data)


from provider.oauth2.models import Client


def app(request):
    data = {}
    if request.user.is_authenticated():
        a = AccessTokenView()
        c = Client.objects.get(pk=1)

        data.update({'access_token': a.get_access_token(request, request.user, 1, c)})
    return render(request, 'app/application.html', data)


# return render(request, 'app/index.html', data)

@api_view(['POST'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((AllowAny,))
def client_reset(request, is_admin_site=False, ):
    form = PasswordResetForm(request.POST)
    if form.is_valid():
        opts = {
            'use_https': request.is_secure(),
            'token_generator': PasswordResetTokenGenerator(),
            'from_email': None,
            'email_template_name': 'registration/password_reset_email.html',
            'subject_template_name': 'registration/password_reset_subject.txt',
            'request': request,
        }
        if is_admin_site:
            opts = dict(opts, domain_override=request.get_host())
        form.save(**opts)

        return HttpResponse(json.dumps({'message': 'Instructions sent to email.'}),
                            content_type="application/json")
    return HttpResponse(json.dumps({'message': 'Email address not found'}), content_type="application/json", status=404)


class RouteEvent(generics.ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (AllowAny,)
    queryset = BackboneRouteEvent.objects.all()
    serializer_class = BackboneRouteEventSerializer

    def pre_save(self, obj):
        if not self.request.user.is_anonymous():
            obj.user = self.request.user


earliest = datetime.datetime(1970, 1, 1, 4, 31)
earliest = timezone.make_aware(earliest, timezone.get_default_timezone())
dthandler = lambda obj: (
    obj.isoformat() if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date)else None)


@api_view(['GET'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((AllowAny,))
def app_version(request, is_admin_site=False, ):
    current_version = App.objects.all()[0].model_version
    data = {'version': current_version}

    if not request.user.is_anonymous():
        latest = get_latest_user_data(request)
        data['user_data_version'] = latest

    return HttpResponse(json.dumps(data, default=dthandler), content_type="application/json")


def get_latest_user_data(request):
    latest_fav, latest_note = earliest, earliest

    # @TODO check project substitution
    if request.user.<%= name %>_favourite.exists():
        latest_fav = request.user.<%= name %>_favourite.latest().timestamp
    if request.user.<%= name %>_note.exists():
        latest_note = request.user.<%= name %>_note.latest().timestamp

    latest = max(latest_fav, latest_note)
    return latest


@api_view(['GET'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((AllowAny,))
def userdata_latest(request, is_admin_site=False, ):
    # look in favs and notes for user data change
    latest = get_latest_user_data(request)

    return HttpResponse(json.dumps({'latest': latest}), content_type="application/json")


class MessageView(PreSaveUserMixin, mixins.CreateModelMixin, GenericAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def pre_save(self, obj):
        """
        Starts a new thread with this message.
        """
        thread = MessageThread()
        thread.save()
        obj.thread = thread

        super(MessageView, self).pre_save(obj)
        serializer = self.get_serializer(object, data=self.request.DATA)

        house = House.objects.get(pk=self.request.DATA[house_serializer_id_field])
        self.set_house_data(self.request, obj, house)

    def post_save(self, message, created=False):
        # after object was saved, we have a key...
        # insert response header
        htmlify_text(message)
        message.text = insert_response_url_header(key=message.key, text=message.text)

        # send message
        logger.info('sending message {} from user {} to user {}'.format(message.pk, message.sender.pk,
                                                                        message.receiver.pk))
        try:
            house_id = self.request.DATA[house_serializer_id_field]

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


def report(request):
    # @TODO check project substitution
    report = ReportService().get_html_report(user=request.user, template='report/report_<%= name %>.html', app_name='<%= name %>')
    return HttpResponse(content=report)


def debug(request):
    if settings.DEBUG:

        data = {}
        if request.user.is_authenticated():
            a = AccessTokenView()
            c = Client.objects.get(pk=1)

            data.update({'access_token': a.get_access_token(request, request.user, 1, c)})
        return render(request, 'app/debug.html', data)
    return redirect('home')