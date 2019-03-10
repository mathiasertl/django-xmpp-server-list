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

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from .forms import CreateServerForm
from .forms import UpdateServerForm
from .models import Server
from .tasks import send_contact_confirmation

log = logging.getLogger(__name__)


class MyServerMixin(LoginRequiredMixin):
    """Makes sure that a ModelView is only called with servers the user owns."""

    queryset = Server.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class IndexView(ListView):
    queryset = Server.objects.moderated().verified().order_by('domain')


class MyServerListView(MyServerMixin, ListView):
    queryset = Server.objects.order_by('domain')
    template_name_suffix = '_list_user'


class ServerCreateView(LoginRequiredMixin, CreateView):
    form_class = CreateServerForm
    model = Server
    queryset = Server.objects.all()
    template_name_suffix = '_create'

    def form_valid(self, form):
        server = form.instance
        owner = self.request.user
        server.user = owner

        # If the servers contact information matches with the users information and it has already been
        # confirmed, we do not need to confirm it again
        if server.contact_type == Server.CONTACT_TYPE_EMAIL and server.contact == owner.email \
                and owner.email_confirmed:
            log.info('Not requesting server confirmation because it matches verified user contact')
            server.contact_verified = True
        elif server.contact_type == Server.CONTACT_TYPE_JID and server.contact == owner.jid \
                and owner.jid_confirmed:
            log.info('Not requesting server confirmation because it matches verified user contact')
            server.contact_verified = True

        # If there is a server with the same contact information, we do not have to verify it again
        elif Server.objects.filter(user=server.user, contact_type=server.contact_type, contact=server.contact,
                                   contact_verified=True):
            log.info('Not requesting server confirmation because it matches another confirmed server')
            server.contact_verified = True

        resp = super().form_valid(form)

        # Send out confirmation if account is not verified
        if not server.contact_verified:
            send_contact_confirmation.delay(server.pk, self.request.get_host(), self.request.is_secure())

        return resp


class ServerUpdateView(MyServerMixin, UpdateView):
    form_class = UpdateServerForm
    template_name_suffix = '_update'


class ServerStatusView(MyServerMixin, DetailView):
    queryset = Server.objects.all()
    template_name_suffix = '_status'


class ModerateView(PermissionRequiredMixin, ListView):
    permission_required = 'server.moderate'
    queryset = Server.objects.order_by('domain').for_moderation()
    template_name = 'server/server_list_moderate.html'


class AjaxServerModerateView(PermissionRequiredMixin, SingleObjectMixin, View):
    http_method_names = ('post', )
    permission_required = 'server.moderate'
    queryset = Server.objects.for_moderation()

    def post(self, request, *args, **kwargs):
        server = self.get_object()
        if request.POST['moderate'] == 'true':
            server.moderated = True
            server.moderation_message = ''
            server.contact_verified = True
        else:
            server.moderated = False
            server.moderation_message = request.POST['message']
        server.save()
        return HttpResponse()
