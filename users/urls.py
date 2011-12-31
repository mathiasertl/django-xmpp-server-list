# -*- coding: utf-8 -*-
#
# This file is part of RestAuth (https://restauth.net).
#
# RestAuth is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RestAuth is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RestAuth.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *
from django.contrib.auth import views 

urlpatterns = patterns(
    'users.views',
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
