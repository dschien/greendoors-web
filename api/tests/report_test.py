import random
from django.contrib.auth.models import User
from django.test import TestCase
import time
from api.models import Scan, House
from greendoors.services.report_service import render_template, ReportService


__author__ = 'schien'


class ReportServiceTests(TestCase):
    """
    API for submitting scans
    """
    fixtures = ['test_data.json']

    def test_get_scan(self):
        user = User.objects.get(pk=1)

        house_objects_all = House.objects.all()
        house = random.choice(house_objects_all)
        #print 'picked house %i' % house.pk
        measure = random.choice(house.measures.all())
        #print 'picked measure %i' % measure.pk

        Scan(user=user, text="%04d%04d" % (house.id, measure.measure.id), timestamp=time.time()).save()

        house = random.choice(house_objects_all)
        measure = random.choice(house.measures.all())
        Scan(user=user, text="%04d%04d" % (house.id, measure.measure.id), timestamp=time.time()).save()

        report = ReportService().get_html_report(user=user)
        print report

    def test_create_url(self):
        user = User.objects.get(pk=1)
        anchor = render_template('trackurl_test_snippet.html', user=user)
        print anchor


