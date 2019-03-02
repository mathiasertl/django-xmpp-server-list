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

from django.urls import path

from server.views import AjaxServerDeleteView
from server.views import AjaxServerModerateView
from server.views import AjaxServerResendView
from server.views import ModerateView
from server.views import MyServerListView
from server.views import ReportView
from server.views import ServerCreateView
from server.views import ServerDetailView
from server.views import ServerUpdateView

app_name = 'server'

urlpatterns = [
    path('', MyServerListView.as_view(), name='list'),
    path('add/', ServerCreateView.as_view(), name='add'),
    path('edit/<int:pk>/', ServerUpdateView.as_view(), name='edit'),
    path('<int:pk>/', ServerDetailView.as_view(), name='view'),
    path('moderate/', ModerateView.as_view(), name='moderate'),

    path('ajax/delete/<int:pk>/', AjaxServerDeleteView.as_view(), name='delete'),
    path('ajax/approve/<int:pk>/', AjaxServerModerateView.as_view(), name='approve'),
    path('ajax/report/<int:pk>/', ReportView.as_view(), name='report'),
    path('ajax/resend/<int:pk>/', AjaxServerResendView.as_view(), name='resend'),
]
