__author__ = 'schien'
from django.conf.urls import patterns, url, include

# Routers provide an easy way of automatically determining the URL conf


urlpatterns = patterns('',
   url(r'^v1/', include('api.urls.urls_v1')),
   url(r'^v2/', include('api.urls.urls_v2')),
)
