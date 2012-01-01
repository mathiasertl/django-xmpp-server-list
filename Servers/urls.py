from django.conf.urls.defaults import *

urlpatterns = patterns(
    'Servers.views',
    url(r'^ajax/$', 'ajax', name='servers_ajax'),
    url(r'^ajax/(?P<server_id>\w+)/$', 'ajax_id', name='servers_ajax_id'),
)