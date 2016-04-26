__author__ = 'schien'
from django.conf.urls import patterns, url, include

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'thirdauth.views.home', name='home'),


)