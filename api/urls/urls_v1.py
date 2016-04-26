from django.conf.urls import patterns, url, include

# Routers provide an easy way of automatically determining the URL conf
from api import views


# override on those views that change from one api version to another
urlpatterns = patterns('',
                       url(r'^app_register$', views.RegisterView.as_view(), name='v1_api_register'),
                       url(r'^', include('api.urls.urls_common')),)
