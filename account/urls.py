# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib.auth import views
from django.contrib.auth.forms import SetPasswordForm

urlpatterns = patterns(
    'account.views',
    url(r'^$', 'index', name='account'),
    url(r'^create/$', 'create', name='account_create'),
    url(r'^edit/$', 'edit', name='account_edit'),
    url(r'^reset_password/$', 'reset_password', name='account_reset_password'),
)
urlpatterns += patterns('',
    url(r'^login/', 'django.contrib.auth.views.login',
        {'template_name': 'account/login.html'}, name='login'),
    url(r'^logout/', 'django.contrib.auth.views.logout',
        {'template_name': 'logout.html'}),
    url(r'^password/', 'django.contrib.auth.views.password_change',
        {'template_name': 'account/set_password.html', 'post_change_redirect': '/user',
         'password_change_form': SetPasswordForm},
        name='account_set_password'
    )
)
