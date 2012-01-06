from django.conf.urls.defaults import *

urlpatterns = patterns(
    'api.views',
    url(r'^$', 'index', name='api'),
    url(r'^help/$', 'help', name='api_help'),
)