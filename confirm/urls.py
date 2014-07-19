# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list)
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
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
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.


from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from confirm.views import UserConfirmationView
from confirm.views import ResetUserPasswordView
from confirm.views import ConfirmServerContactView


urlpatterns = patterns(
    'confirm.views',
    url(r'^user/contact/(?P<key>\w+)/$', UserConfirmationView.as_view(),
        name='confirm_user_contact'),
    url(r'^user/password/(?P<key>\w+)/$', ResetUserPasswordView.as_view(),
        name='reset_user_password'),
    url(r'^server/(?P<key>\w+)/$', login_required(ConfirmServerContactView.as_view()),
        name='confirm_server'),
)
