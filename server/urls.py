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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.conf.urls import patterns
from django.conf.urls import url

from server.views import EditView
from server.views import ModerateView
from server.views import ReportView
from server.views import ResendView
from server.views import AjaxServerUpdateView
from server.views import AjaxServerDeleteView


urlpatterns = patterns(
    'server.views',
    url(r'^$', login_required(EditView.as_view()), name='server'),
    url(r'^moderate/$', permission_required('server.moderate')(ModerateView.as_view()),
        name='server_moderation'),

    url(r'^ajax/$', 'ajax', name='server_create'),
    url(r'^ajax/delete/(?P<pk>\w+)/$', AjaxServerDeleteView.as_view(), name='server_delete'),
    url(r'^ajax/moderate/$', 'ajax_moderate', name='server_moderate'),
    url(r'^ajax/report/(?P<pk>\w+)$', ReportView.as_view(), name='server_report'),
    url(r'^ajax/resend/$', login_required(ResendView.as_view()), name='server_resend'),
    url(r'^ajax/update/(?P<pk>\w+)/$', AjaxServerUpdateView.as_view(), name='server_update'),
)
