from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from rest_framework.reverse import reverse
from api.models import RedirectUrl
from greendoors.services import UrlTrackingService

__author__ = 'schien'


class RedirectionTest(TestCase):
    """
    API functions for app login
    """
    fixtures = ['test_data.json']

    def test_redirection_anonymous(self):
        url = 'http://www.google.de'
        username = User.objects.all()[0].username
        redirect = UrlTrackingService.generate_redirect_url(target_url=url, username=username, display_text="google")

        response = self.client.get(reverse('api_redirect', kwargs={'key': redirect.redirect_key}))

        manager = RedirectUrl.objects.filter(redirect_key__exact=redirect.redirect_key)

        self.assertTrue(len(manager) == 1)
        redirect = manager[0]

        click_set_all = redirect.clicks.all()
        self.assertTrue(len(click_set_all) == 1)
        print click_set_all[0].time

        self.assertTrue(response.status_code == 301)




