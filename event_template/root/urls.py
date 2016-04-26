from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
# @TODO check project substitution
from <%= name %> import views
from <%= name %>.views import HouseView, HouseDetail, MeasureView, MeasureDetail, MeasureCategoryView, \
    MeasureCategoryDetail, FavouriteView, FavouriteDetail, NoteDetail, NoteView, \
    ScanView, RouteEvent, MessageView


__author__ = 'schien'
from django.conf.urls import patterns, url, include




#            contacts: backend + "contacts/",
#            settings: backend + "settings/"

#user_urls = patterns('',
#                     url(r'^/(?P<username>[0-9a-zA-Z_-]+)/posts$', UserPostList.as_view(), name='userpost-list'),
#                     url(r'^/(?P<username>[0-9a-zA-Z_-]+)$', UserDetail.as_view(), name='user-detail'),
#                     url(r'^$', UserList.as_view(), name='user-list')
#)

code_url = patterns('',
                    url(r'^/(?P<scan>[0-9]+)$', views.detail, name='code'),
)

measure_urls = patterns('',

                        url(r'^/(?P<pk>[0-9]+)$', MeasureDetail.as_view(), name='measure-detail'),
                        url(r'^$', MeasureView.as_view(), name='measures-list'),
)

measurecategory_urls = patterns('',

                                url(r'^/(?P<pk>[0-9]+)$', MeasureCategoryDetail.as_view(),
                                    name='measurecategory-detail'),
                                url(r'^$', MeasureCategoryView.as_view(), name='measurecategories-list'),
)

favourite_urls = patterns('',

                          url(r'^/(?P<pk>[0-9]+)$', FavouriteDetail.as_view(), name='favourite-detail'),
                          url(r'^$', FavouriteView.as_view(), name='favourites-list'),
)

scan_urls = patterns('',

                     url(r'^$', ScanView.as_view(), name='scan-list'),
)

note_urls = patterns('',

                     url(r'^/(?P<pk>[0-9]+)$', NoteDetail.as_view(), name='note-detail'),
                     url(r'^$', NoteView.as_view(), name='note-list'),
)

house_urls = patterns('',

                      url(r'^/(?P<pk>[0-9]+)$', HouseDetail.as_view(), name='house-detail'),
                      url(r'^$', HouseView.as_view(), name='houses-list'),
)

# webnotes_urls = patterns('',
#                          url(r'^notes$', login_required(NotesListView.as_view(template_name="greendoors/notes.html")),
#                              name='notes'),
#
#
#                          url(r'note/add/$', login_required(NoteCreate.as_view()), name='note_add'),
#                          url(r'note/(?P<pk>\d+)/$', login_required(NoteUpdate.as_view()), name='note'),
#                          url(r'note/(?P<pk>\d+)/delete/$', login_required(NoteDelete.as_view()), name='note_delete'),
#
# )

urlpatterns = patterns('',
                       # @TODO check project substitution
                       url(r'^$', TemplateView.as_view(template_name='<%= name %>/index.html'), name='home'),
                       url(r'^app', views.app, name='app'),
                       url(r'contact$', TemplateView.as_view(template_name='<%= name %>/contact.html'), name='contact'),
                       url(r'downloads$', TemplateView.as_view(template_name='<%= name %>/downloads.html'), name='downloads'),
                       url(r'reports$', TemplateView.as_view(template_name='<%= name %>/reports.html'), name='reports'),
                       url(r'qrcodes$', TemplateView.as_view(template_name='<%= name %>/qrcodes.html'), name='qrcodes'),
                       url(r'^report$', login_required(views.report), name='report'),
                       url(r'^useraction$', RouteEvent.as_view(), name='user-action'),
                       url(r'^message$', MessageView.as_view(), name='message'),
                       url(r'^app_version$', views.app_version, name='app-version'),
                       url(r'^userdata_latest$', views.userdata_latest, name='userdata_latest'),
                       url(r'^code', include(code_url)),
                       url(r'^houses', include(house_urls)),
                       url(r'^notes', include(note_urls)),
                       url(r'^measures', include(measure_urls)),
                       url(r'^scans', include(scan_urls)),
                       url(r'^favourites', include(favourite_urls)),
                       url(r'^reset_password', views.client_reset, name='password-reset'),
                       url(r'^measurecategories', include(measurecategory_urls)),
                       url(r'^debug', views.debug),

)
