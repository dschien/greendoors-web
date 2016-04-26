from django.conf.urls import patterns, url

# Routers provide an easy way of automatically determining the URL conf

from api import views
from api.views import TrackingRedirectView


urlpatterns = patterns('',


                       url(r'^app_register$', views.RegisterView.as_view(), name='app_register'),

                       url(r'^check_username$', views.check_username, name='app_check_username'),

                       url(r'^logger$', views.log_message, name='app_log_message'),

                       url(r'^fav$', views.BulkFavList.as_view(), name='app_favourite'),

                       url(r'^note$', views.BulkNoteList.as_view(), name='app_note'),


                       url(r'^scan$', views.BulkScan.as_view(), name='app_bulk_scan'),

                       url(r'^scan/(?P<pk>[0-9]+)/$', views.BulkScan.as_view(), name='scan_detail'),

                       url(r'^note/(?P<pk>[0-9]+)/$', views.BulkNoteList.as_view(), name='note_detail'),

                       url(r'^message$', views.BulkMessageView.as_view(), name='app_message'),

                       url(r'^phone/$', views.PhoneCreate.as_view(), name='app_phone'),

                       url(r'^update/$', views.DataView.as_view(), name='api_update'),


                       url(r'^url/(?P<key>[0-9a-z\-]+)/$', TrackingRedirectView.as_view(), name='api_redirect'),

                       # url(r'^mail/(?P<key>[0-9]+)/$', TrackingRedirectView.as_view(), name='api_redirect'),

                       url(r'^url_gen/$', views.create_url, name='api_generate_url'),

                       url(r'^register-by-token/(?P<backend>[^/]+)/$', 'api.views.register_by_access_token',
                           name='register_by_access_token')


)
