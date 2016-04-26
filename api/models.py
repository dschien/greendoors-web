import random
import string
import datetime

from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse
from tinymce.models import HTMLField


__author__ = 'schien'

import re

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from django.db import models
from django.forms import fields
from django.forms import ValidationError
from django.utils.encoding import smart_unicode

from django_extensions.db.fields import UUIDField


class HexColorField(fields.Field):
    default_error_messages = {
        'hex_error': u'This is an invalid color code. It must be a html hex color code e.g. #000000'
    }

    def clean(self, value):

        super(HexColorField, self).clean(value)

        if value in fields.EMPTY_VALUES:
            return u''

        value = smart_unicode(value)
        value_length = len(value)

        if value_length != 7 or not re.match('^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', value):
            raise ValidationError(self.error_messages['hex_error'])

        return value

    def widget_attrs(self, widget):
        if isinstance(widget, (fields.TextInput)):
            return {'maxlength': str(7)}


class UserProfile(models.Model):
    """
    Message between two users
    """
    user = models.OneToOneField(User, verbose_name="django authentication user", related_name='user_profile')
    newsletter = models.NullBooleanField(null=False, blank=False)
    research = models.NullBooleanField(null=False, blank=False)

    def __unicode__(self):
        return "%s " % self.user.username


class TrackableURL(models.Model):
    url = models.URLField(max_length=255, unique=True)

    def __unicode__(self):
        return self.url


class RelatedTrackableURL(TrackableURL):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.url


class RedirectUrl(models.Model):
    redirect_key = UUIDField(unique=True, auto=True)
    target_url = models.ForeignKey(TrackableURL, related_name='redirect_urls')
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='links')

    def __unicode__(self):
        return "%s %s %s" % (self.user.username, self.redirect_key, self.target_url.url)

    class Meta:
        unique_together = ('target_url', 'user')


class Click(models.Model):
    redirect = models.ForeignKey(RedirectUrl, verbose_name="redirection url", related_name='clicks')
    time = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.redirect.user.username, self.redirect.target_url.url, self.time)


class Scan(models.Model):
    """
    Barcode scans
    """
    created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=8)
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='scans')
    # timestamp = models.BigIntegerField()

    class Meta:
        ordering = ('created',)
        # unique_together = ('user', 'text', 'timestamp')

    def __unicode__(self):
        return u'%s %s' % (self.text, self.user.username)

    @property
    def house(self):
        return House.objects.get(pk=int(self.text[0:4]))


    @property
    def measure(self):
        m = int(self.text[5:8])
        if m > 0:
            measure = Measure.objects.get(pk=m)
            imeasure = InstalledMeasure.objects.filter(house=self.house, measure=measure)[0]
            return imeasure
        return None


class Device(models.Model):
    """
    UUID from devices
    """
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='phones')
    uuid = models.CharField(null=True, blank=True, max_length=40)

    cordova = models.CharField(null=True, blank=True, max_length=400)
    platform = models.CharField(null=True, blank=True, max_length=400)
    version = models.CharField(null=True, blank=True, max_length=400)
    model = models.CharField(null=True, blank=True, max_length=400)

    def __unicode__(self):
        return u'%s %s %s' % (self.user.username, self.platform, self.version)


class HomeOwnerProfile(models.Model):
    """

    """
    user = models.OneToOneField(User, verbose_name="django authentication user", related_name='home_owner_profile')


class MeasureCategory(models.Model):
    """
    A measure category
    """
    name = models.TextField()
    is_renewable = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % (self.name, )


class Measure(models.Model):
    """
    A measure
    """
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    short = models.CharField(max_length=80, null=True)
    color = models.CharField(max_length=7, null=True, blank=True)
    category = models.ForeignKey(MeasureCategory, related_name='measures')

    report_template = models.CharField(max_length=200, default='report/general_measure_text.html')

    def __unicode__(self):
        return u'%s' % (self.name,)


class House(models.Model):
    """
    Houses
    """
    owner = models.ForeignKey(HomeOwnerProfile, verbose_name="home owner profile", related_name='house', null=True)
    address = models.CharField(max_length=1024)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    adults = models.IntegerField(null=True)
    children = models.IntegerField(null=True)
    bedrooms = models.IntegerField(null=True)
    comments = models.CharField(max_length=1024, null=True, blank=True)

    OPEN_SATURDAY_AND_SUNDAY = 3
    OPEN_SUNDAY = 2
    OPEN_SATURDAY = 1
    OPEN_CLOSED = 0

    OPEN_CHOICES = (
        (OPEN_CLOSED, 'Closed'),
        (OPEN_SATURDAY, 'Saturday'),
        (OPEN_SUNDAY, 'Sunday'),
        (OPEN_SATURDAY_AND_SUNDAY, 'Saturday and Sunday'),
    )

    open = models.IntegerField(max_length=1, choices=OPEN_CHOICES, null=True)

    ACCESSIBILITY_FULL = 1
    ACCESSIBILITY_PARTIAL = 2
    ACCESSIBILITY_NONE = 0

    ACCESSIBILITY_CHOICES = (
        (ACCESSIBILITY_FULL, 'Full'),
        (ACCESSIBILITY_PARTIAL, 'Partial'),
        (ACCESSIBILITY_NONE, 'None')
    )

    accessibility = models.IntegerField(max_length=1, choices=ACCESSIBILITY_CHOICES, null=True)

    AGE_VICTORIAN = 1
    AGE_30s = 3
    AGE_50s = 5
    AGE_70s = 7
    AGE_NEW = 8
    AGE_GEORGIAN = 0
    AGE_20s = 2
    AGE_60s = 6

    AGE_CHOICES = ((AGE_VICTORIAN, "Victorian"),
                   (AGE_30s, "1930s"),
                   (AGE_50s, "1950s"),
                   (AGE_70s, "1970s"),
                   (AGE_NEW, "New"),
                   (AGE_GEORGIAN, "Georgian"),
                   (AGE_20s, "1920s"),
                   (AGE_60s, "1960s"))

    age = models.IntegerField(max_length=1, choices=AGE_CHOICES, null=True)

    TYPE_MULTI_OCCUPANT = 5
    TYPE_DETACHED = 1
    TYPE_BUNGALOW = 4
    TYPE_TERRACE = 3
    TYPE_SEMI = 2

    TYPE_CHOICES = ((TYPE_MULTI_OCCUPANT, "Multi Occupant"),
                    (TYPE_DETACHED, "Detached"),
                    (TYPE_BUNGALOW, "Bungalow"),
                    (TYPE_TERRACE, "Terrace"),
                    (TYPE_SEMI, "Semi")
    )

    type = models.IntegerField(max_length=1, choices=TYPE_CHOICES, null=True)

    CONTACT_NONE = 0
    CONTACT_YEAR = 2
    CONTACT_MONTH = 1
    CONTACT_CHOICES = (
        (CONTACT_NONE, "None"),
        (CONTACT_YEAR, "Year"),
        (CONTACT_MONTH, "Month")
    )

    contact = models.IntegerField(max_length=1, choices=CONTACT_CHOICES, default=CONTACT_NONE, null=True)

    MAPPING_MONTH = 1
    MAPPING_YEAR = 2
    MAPPING_CHOICES = ((MAPPING_MONTH, "Month"), (MAPPING_YEAR, "Year"))

    mapping = models.IntegerField(max_length=1, choices=MAPPING_CHOICES, null=True)

    image = models.TextField()

    report_text = models.TextField(null=True, blank=True)
    # urls = GenericRelation(RelatedTrackableURL, null=True, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.pk, self.address)


class Note(models.Model):
    """
    Notes for houses
    """
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='notes')
    house = models.ForeignKey(House, related_name='note')
    timestamp = models.BigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('created',)
        unique_together = ('user', 'house')

    def __unicode__(self):
        return u'%s %s' % (self.house.id, self.text)

    def get_absolute_url(self):
        return reverse('web:note', kwargs={'pk': self.pk})


class InstalledMeasure(models.Model):
    measure = models.ForeignKey(Measure)
    cost = models.IntegerField(null=True, blank=True)
    disruption = models.IntegerField(null=True, blank=True)
    house = models.ForeignKey(House, null=True, blank=True, related_name='measures')

    report_text = models.TextField(null=True, blank=True)
    supplier = models.CharField(max_length=1024, null=True, blank=True)
    supplier_urls = GenericRelation(RelatedTrackableURL, null=True, blank=True, related_name='supplier_urls')
    product = models.CharField(max_length=1024, null=True, blank=True)
    product_urls = GenericRelation(RelatedTrackableURL, null=True, blank=True, related_name='product_urls')

    def __unicode__(self):
        return u'%s' % (self.measure.short,)


class MessageThread(models.Model):
    pass


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


DEFAULT_THREAD_ID = 1


class Message(models.Model):
    """
    Message between two users
    """
    created = models.DateTimeField(auto_now_add=True)
    text = HTMLField()
    sender = models.ForeignKey(User, verbose_name="sending django authentication user", related_name='sent_messages')
    receiver = models.ForeignKey(User, verbose_name="receiving django authentication user",
                                 related_name='received_messages')
    sent = models.BooleanField(default=False)
    thread = models.ForeignKey(MessageThread, default=DEFAULT_THREAD_ID, related_name='messages')
    key = UUIDField(auto=True)

    class Meta:
        ordering = ('created',)
        unique_together = ('sender', 'created')

    def __unicode__(self):
        return u'%s %s' % (self.text, self.sent)


class Favourite(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='favourites')
    house = models.ForeignKey(House, null=True)
    timestamp = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'house')

    def __unicode__(self):
        return u'%s' % (self.house.address,)


class App(models.Model):
    model_version = models.CharField(max_length=8, unique=True)
    openday = models.DateField(default=datetime.date(day=26, month=9, year=2013))


class MessageKey(models.Model):
    """
    Provides a url key to compose a message as response
    """
    message_key = models.BigIntegerField(unique=True)
    previous_message = models.ForeignKey(Message)


class LoggerMessage(models.Model):
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="django user", related_name='log_messages', null=True, blank=True)

    def __unicode__(self):
        return u'%s %s %s' % (self.created, self.user, self.message[:80])
