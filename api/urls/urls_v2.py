from django.conf.urls import patterns, url, include

# Routers provide an easy way of automatically determining the URL conf


# override on those views that change from one api version to another
urlpatterns = patterns('',
                       url(r'^', include('api.urls.urls_common')),
)
