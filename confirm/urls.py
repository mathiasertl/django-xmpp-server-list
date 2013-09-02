# -*- coding: utf-8 -*-
#
# This file is part of xmpplist (https://list.jabber.at).
#
# xmpplist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmpplist.  If not, see <http://www.gnu.org/licenses/>.


from django.conf.urls.defaults import *
from django.contrib.auth import views

urlpatterns = patterns(
    'confirm.views',
    url(r'^user/contact/(?P<key>\w+)/$', 'confirm_user_contact', name='confirm_user_contact'),
    url(r'^user/password/(?P<key>\w+)/$', 'reset_user_password', name='reset_user_password'),
    url(r'^server/(?P<key>\w+)/$', 'confirm_server', name='confirm_server'),
)
