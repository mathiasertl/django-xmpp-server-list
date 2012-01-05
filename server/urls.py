from django.conf.urls.defaults import *

urlpatterns = patterns(
    'server.views',
    url(r'^$', 'index', name='server'),
    url(r'^moderate/$', 'moderate', name='server_moderate'),
    url(r'^(?P<server_id>\w+)/report/$', 'report', name='server_report'),
    
    url(r'^ajax/$', 'ajax', name='servers_ajax'),
    url(r'^ajax/mapbrowse/$', 'ajax_mapbrowse', name='server_ajax_mapbrowse'),
    url(r'^ajax/moderate/$', 'ajax_moderate', name='server_ajax_moderate'),
    url(r'^ajax/(?P<server_id>\w+)/$', 'ajax_id', name='servers_ajax_id'),
    url(r'^ajax/(?P<server_id>\w+)/mapbrowse/$', 'ajax_id_mapbrowse', name='server_ajax_id_mapbrowse'),
)