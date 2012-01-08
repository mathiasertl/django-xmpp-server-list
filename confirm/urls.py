# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib.auth import views 

urlpatterns = patterns(
    'confirm.views',
    url(r'^user/contact/(?P<key>\w+)/$', 'confirm_user_contact', name='confirm_user_contact'),
    url(r'^user/password/(?P<key>\w+)/$', 'reset_user_password', name='reset_user_password'),
    url(r'^server/(?P<key>\w+)/$', 'confirm_server', name='confirm_server'),
)