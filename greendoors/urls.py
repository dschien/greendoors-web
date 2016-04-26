from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from django.views.generic.base import TemplateView

from greendoors.views import ActivationView, RegistrationViewGreendoors
from registration.backends.default.views import RegistrationView
admin.autodiscover()

registration_patterns = patterns('',
                       url(r'^activate/complete/$',
                           TemplateView.as_view(template_name='registration/activation_complete.html'),
                           name='registration_activation_complete'),
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "invalid key" message instead of a
                       # confusing 404.
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           ActivationView.as_view(),
                           name='registration_activate'),
                       url(r'^register/$',
                           RegistrationViewGreendoors.as_view(),
                           name='registration_register'),
                       url(r'^register/complete/$',
                           TemplateView.as_view(template_name='registration/registration_complete.html'),
                           name='registration_complete'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
                       (r'', include('registration.auth_urls')),
)

urlpatterns = patterns('',
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       url(r'^admin/', include(admin.site.urls)),

                       url(r'^api/', include('api.urls.urls')),

                       url(r'^', include('web.urls', namespace="web")),
                       url(r'^swilt2014/', include('south_wiltshire_2014.urls', namespace='swilt2014')),
                       url(r'^frome2014/', include('frome2014.urls',namespace='frome2014')),
                       url(r'^bristol2013/', include('bristol2013.urls', namespace='bristol2013')),
                       url(r'^bristol2014/', include('bristol2014.urls', namespace='bristol2014')),


                       url(r'^thirdauth/', include('thirdauth.urls', namespace='thirdauth')),

                       url(r'^social_login/', include('social.apps.django_app.urls', namespace='social')),

                       url('', include('django.contrib.auth.urls', namespace='auth')),
                       url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
                       url(r'^accounts/', include(registration_patterns)),

                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                       url(r'^tinymce/', include('tinymce.urls')),
#                       url(r'^report_builder/', include('report_builder.urls'))

)