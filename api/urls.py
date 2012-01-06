from django.conf.urls.defaults import *

urlpatterns = patterns(
    'api.views',
    url(r'^$', 'index', name='api'),
)