# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib.auth import views 

urlpatterns = patterns(
    'account.views',
    url(r'^$', 'index', name='users'),
    url(r'^create/$', 'create', name='users_create'),
    url(r'^confirm_email/(?P<key>\w+)/$', 'confirm_email', name='users_confirm_email'),
    url(r'^edit/$', 'edit', name='users_edit'),
    url(r'^set_password/$', 'set_password', name='users_set_password'),
    url(r'^reset_password/$', 'reset_password', name='users_reset_password'),
)
urlpatterns += patterns('',
    url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
)
