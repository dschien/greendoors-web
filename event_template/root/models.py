import random
import re
import string
import datetime

from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver
import tldextract
from dbtemplates.models import Template

from api.models import RelatedTrackableURL


__author__ = 'schien'

from django.contrib.auth.models import User
from django.db import models


class Scan(models.Model):
    """
    Barcode scans
    """
    created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=8)
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='%(app_label)s_%(class)s')
    # timestamp = models.DateTimeField()

    class Meta:
        ordering = ('created',)
        unique_together = ('user', 'text')

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


class HomeOwnerProfile(models.Model):
    """

    """
    user = models.OneToOneField(User, verbose_name="django authentication user", related_name='%(app_label)s_%(class)s')

    def __unicode__(self):
        return u'%s' % (self.user.username, )


class House(models.Model):
    """
    Houses
    """
    owner = models.ForeignKey(HomeOwnerProfile, verbose_name="home owner profile",
                              related_name='%(app_label)s_%(class)s', null=True)
    address = models.CharField(max_length=1024)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    booking = models.IntegerField(null=True)
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

    day = models.IntegerField(max_length=1, choices=OPEN_CHOICES, null=True)

    TIME_A = 1
    TIME_B = 2
    TIME_CHOICES = (
        (TIME_A, '10-15'),
        (TIME_B, '8-9'),
    )

    time = models.IntegerField(max_length=1, choices=TIME_CHOICES, null=True, blank=True)

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

    image = models.TextField(null=True, blank=True)

    report_text = models.TextField(null=True, blank=True)
    final_notes = models.TextField(null=True, blank=True)
    # urls = GenericRelation(RelatedTrackableURL, null=True, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.pk, self.address)


class Note(models.Model):
    """
    Notes for houses
    """
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='%(app_label)s_%(class)s')
    house = models.ForeignKey(House, related_name='%(app_label)s_%(class)s')
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ('created',)
        unique_together = ('user', 'house')
        get_latest_by = "timestamp"

    def __unicode__(self):
        return u'%s %s' % (self.house.id, self.text)

    def get_absolute_url(self):
        return reverse('web:note', kwargs={'pk': self.pk})


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


class InstalledMeasure(models.Model):
    measure = models.ForeignKey(Measure, related_name='installed_measure')
    cost = models.IntegerField(null=True, blank=True)
    disruption = models.IntegerField(null=True, blank=True)
    house = models.ForeignKey(House, null=True, blank=True, related_name='measures')
    extras = models.TextField(null=True, blank=True)
    report_text = models.TextField(null=True, blank=True)

    # generated template text with trackable urls
    supplier_template = models.ForeignKey(Template, related_name='%(app_label)s_%(class)s_measure_supplier', null=True, blank=True)

    # text from the house holder
    supplier = models.TextField(null=True, blank=True)
    # urls fished out by us - possibly several
    supplier_urls_text = models.TextField(null=True, blank=True)

    supplier_urls = GenericRelation(RelatedTrackableURL, null=True, blank=True,
                                    related_name='%(app_label)s_%(class)s_supplier_urls')

    # generated template text with trackable urls
    product_template = models.ForeignKey(Template, related_name='%(app_label)s_%(class)s_measure_product', null=True, blank=True)

    # text from the house holder
    product = models.TextField(null=True, blank=True)

    # urls fished out by us - possibly several
    product_urls_text = models.TextField(null=True, blank=True)

    product_urls = GenericRelation(RelatedTrackableURL, null=True, blank=True,
                                   related_name='%(app_label)s_%(class)s_product_urls')

    @property
    def disruptionText(self):
        if self.disruption == 1:
            return 'low'
        if self.disruption == 2:
            return 'medium'
        if self.disruption == 3:
            return 'high'

        return ""

    def __unicode__(self):
        return u'%s' % (self.measure.short,)


def create_template_text(display_text, urls_text, text):
    empty_text = 'Unknown'
    track_url_pattern = "{{% trackurl '{0}' '{1}' %}}"

    print display_text, urls_text

    if urls_text:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                          urls_text)
        # two urls - put at the beginngin
        if len(urls) > 1:
            for url in urls:
                text += track_url_pattern.format(url, tldextract.extract(url).domain.capitalize()) + "\n"

            if display_text:
                text += str(display_text)
        # only one url - make the whole text a link
        else:
            text = track_url_pattern.format(urls[0], str(display_text)) + "\n"
    # no urls
    else:
        text += str(display_text) if display_text else empty_text
    return text


@receiver(pre_save, sender=InstalledMeasure)
def generate_linked_text(sender, instance, *args, **kwargs):
    print 'creating template for house {0} measure {1}'.format(instance.house.pk, instance.measure)

    text = ""
    text = create_template_text(instance.supplier, instance.supplier_urls_text, text)

    template, _ = Template.objects.get_or_create(
        name=instance._meta.app_label + "_" + str(instance.house.pk) + "_" + instance.measure.short.replace(" ",
                                                                                                            "_") + "_supplier")
    print "supplier text: %s from %s and %s" % (text, instance.supplier, instance.supplier_urls_text)
    template.content = text
    template.save()
    instance.supplier_template = template

    text = ""
    text = create_template_text(instance.product, instance.product_urls_text, text)

    template, _ = Template.objects.get_or_create(
        name=instance._meta.app_label + "_" + str(instance.house.pk) + "_" + instance.measure.short.replace(" ",
                                                                            "_") + "_product")
    print "product text: %s from %s and %s" % (text, instance.product, instance.product_urls_text)
    template.content = text
    template.save()
    instance.product_template = template


class MessageThread(models.Model):
    pass


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


DEFAULT_THREAD_ID = 1


class Favourite(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='%(app_label)s_%(class)s')
    house = models.ForeignKey(House, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'house')
        get_latest_by = "timestamp"

    def __unicode__(self):
        return u'%s' % (self.house.address,)


class App(models.Model):
    model_version = models.CharField(max_length=8, unique=True)
    openday = models.DateField(default=datetime.date(day=26, month=9, year=2013))


class BackboneRouteEvent(models.Model):
    route = models.CharField(max_length=120)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, verbose_name="django authentication user", related_name='%(app_label)s_%(class)s',
                             null=True, blank=True)
    device = models.CharField(max_length=1024)