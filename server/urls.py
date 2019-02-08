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

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from server.views import AjaxServerCreateView
from server.views import AjaxServerDeleteView
from server.views import AjaxServerModerateView
from server.views import AjaxServerResendView
from server.views import AjaxServerResubmitView
from server.views import AjaxServerUpdateView
from server.views import EditView
from server.views import ModerateView
from server.views import ReportView

# TODO: use path instead of url
# TODO: use namespace instead of name prefix
# TODO: move decorators to class
urlpatterns = [
    url(r'^$', login_required(EditView.as_view()), name='server'),
    url(r'^moderate/$', permission_required('server.moderate')(ModerateView.as_view()),
        name='server_moderation'),

    url(r'^ajax/$', AjaxServerCreateView.as_view(), name='server_create'),
    url(r'^ajax/delete/(?P<pk>\w+)/$', AjaxServerDeleteView.as_view(), name='server_delete'),
    url(r'^ajax/moderate/(?P<pk>\w+)/$', AjaxServerModerateView.as_view(), name='server_moderate'),
    url(r'^ajax/report/(?P<pk>\w+)$', ReportView.as_view(), name='server_report'),
    url(r'^ajax/resend/(?P<pk>\w+)$', AjaxServerResendView.as_view(), name='server_resend'),
    url(r'^ajax/resubmit/(?P<pk>\w+)$', AjaxServerResubmitView.as_view(), name='server_resubmit'),
    url(r'^ajax/update/(?P<pk>\w+)/$', AjaxServerUpdateView.as_view(), name='server_update'),
]
